from pathlib import Path
from information import info
from warning import warn
from demucs.pretrained import get_model
from demucs.audio import AudioFile, save_audio
from demucs.apply import apply_model
from huggingface_hub import hf_hub_download
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from safetensors.torch import load_file
from deep_translator import GoogleTranslator

import yaml
import torch
import gc
import ffmpeg
import whisper
import torchaudio as ta
import subprocess
import shlex
import shutil
import time

with open("configuration.yaml", "r") as configuration:

    config = yaml.safe_load(configuration)

script_path = Path(__file__).resolve().parent

audio_path = script_path / config["paths"]["audios"]
ffmpeg_path = audio_path / config["paths"]["ffmpeg"]

demucs_path = audio_path / config["paths"]["demucs"]
demucs_wav = demucs_path / config["paths"]["demucs_wav"]
demucs_segments = demucs_path / config["paths"]["segments"]

dubbed_path = audio_path / config["paths"]["dubbed"]
dubbed_segments = dubbed_path / config["paths"]["segments"]

videos_path = script_path / config["paths"]["videos"]
video_segments = videos_path / config["paths"]["segments"]

dubbed_videos = videos_path / config["paths"]["dubbed"]
latentsync_path = script_path / config["paths"]["latentsync"]

concat_file = script_path / config["paths"]["concat"]

created_dirs = [

    audio_path, 
    ffmpeg_path, 
    demucs_path,
    demucs_segments,
    dubbed_path,
    dubbed_segments,
    videos_path,
    video_segments,
    dubbed_videos

    ]

deleted_dirs = [

    audio_path,
    ffmpeg_path,
    demucs_path,
    dubbed_path,
    videos_path

    ]

for directory in created_dirs:
    
    if not directory.exists():

        directory.mkdir(parents=True, exist_ok=True)

cuda = torch.cuda.is_available()
processing_device = "cuda" if cuda else "cpu"

def flush():

    gc.collect()

    if cuda:

        torch.cuda.empty_cache()

class Dubbing:

    def __init__(self, source_video, language, progression):

        self.source_video = source_video
        self.language = language
        self.update = progression
        self.detected_language = None
        self.segments_list = []

    def extract_audio(self):

        try: 

            (
                ffmpeg
                .input(self.source_video)
                .output(

                    str(ffmpeg_path / "ffmpeg.wav"),
                    acodec="pcm_s32le",
                    ar="44100",
                    ac=2

                )

                 .run(overwrite_output=True, quiet=True)
            )

        except Exception:
            
            warn("An error occurred while extracting the audio track from the video !")

    def separate_vocals(self):

        demucs_model = get_model(name=config["models"]["demucs"])
        demucs_model.to(processing_device).eval()

        try:

            ffmpeg_audio = AudioFile(str(ffmpeg_path / "ffmpeg.wav")).read(
                
                streams=[0],
                samplerate=demucs_model.samplerate,
                channels=demucs_model.audio_channels

                )

        except Exception:

            warn("An error occurred while processing the audio file by Demucs !")
            return
        
        with torch.no_grad():

            audio_squeeze = ffmpeg_audio.to(processing_device)

            separated_sources = apply_model(

                demucs_model,
                audio_squeeze

                )[0]
            
            voice_track = demucs_model.sources.index("vocals")
            audio_position = separated_sources[voice_track]

            save_audio(

                audio_position.cpu(),
                str(demucs_wav),
                samplerate=demucs_model.samplerate
            
                )
            
            del demucs_model, separated_sources, audio_squeeze, audio_position
            flush()

    def detect_language(self):

        whisper_model = whisper.load_model(config["models"]["whisper"], device=processing_device)

        audio_data = whisper.load_audio(str(demucs_wav))
        audio_data = whisper.pad_or_trim(audio_data)

        mel_spectrogram = whisper.log_mel_spectrogram(
            
            audio_data, 
            n_mels=whisper_model.dims.n_mels).to(whisper_model.device)

        _, probabilities = whisper_model.detect_language(mel_spectrogram)
        self.detected_language = max(probabilities, key=probabilities.get)

        del whisper_model, audio_data, mel_spectrogram
        flush()

    def transcribe_audio(self):

        whisper_model = whisper.load_model(config["models"]["whisper"], device=processing_device)

        transcription = whisper_model.transcribe(
            
            str(demucs_wav),
            word_timestamps=True
            
            )
        
        del whisper_model
        flush()

        combined_segments = []
        current_segment = None

        for segment in transcription["segments"]:

            if current_segment is None:

                current_segment = segment

            else:

                current_segment["text"] += " " + segment["text"]
                current_segment["end"] = segment["end"]

            if segment["text"].strip().endswith((".", "?", "!")):

                combined_segments.append(current_segment)
                current_segment = None

        if current_segment:

            combined_segments.append(current_segment)

        self.segments_list = combined_segments

    def prepare_tts(self):

        if self.language == "fr":

            french_model = hf_hub_download(

                repo_id="Thomcles/Chatterbox-TTS-French", 
                filename="t3_cfg.safetensors"

                )

            chatterbox_model = ChatterboxMultilingualTTS.from_pretrained(device=processing_device)
            model_weights = load_file(

                french_model,
                device="cpu"

                )

            chatterbox_model.t3.load_state_dict(model_weights)
            del model_weights

        else:

            chatterbox_model = ChatterboxMultilingualTTS.from_pretrained(device=processing_device)

        translator = GoogleTranslator(source=self.detected_language, target=self.language)

        return chatterbox_model, translator

    def process_segments(self, chatterbox_model, translator):

        segments_count = len(self.segments_list)

        for index, segment in enumerate(self.segments_list, start=1):

            success = False
            attempts = 0

            while not success and attempts < 3:

                try:
                    
                    attempts += 1
                    start_time = segment["start"]
                    end_time = segment["end"]
                    duration = max(0.1, end_time - start_time)
                    
                    audio_segment = demucs_segments / f"audio_{index}.wav"

                    (
                        ffmpeg
                        .input(str(demucs_wav), ss=start_time, t=duration)
                        .output(str(audio_segment), acodec="pcm_s16le", ar="44100")
                        .run(overwrite_output=True, quiet=True)
                    )

                    video_segment = video_segments / f"video_{index}.mp4"
                    
                    (
                        ffmpeg
                        .input(self.source_video, ss=start_time, t=duration)
                        .output(

                            str(video_segment), 
                            vcodec="libx264", 
                            preset="veryfast", 
                            crf=18, 
                            movflags="+faststart", 
                            pix_fmt="yuv420p", 
                            acodec="aac", 
                            audio_bitrate="320k"
                            
                            )

                        .run(overwrite_output=True, quiet=True)
                    )

                    translated_text = translator.translate(segment["text"])
                    temp_audio = dubbed_segments / f"temp_{index}.wav"
                    dubbed_audio = dubbed_segments / f"dubbed_audio-{index}.wav"

                    wav = chatterbox_model.generate(

                        translated_text, 
                        language_id=self.language,
                        audio_prompt_path=str(audio_segment)
                        
                        )

                    ta.save(str(temp_audio), wav.cpu(), chatterbox_model.sr)
                    del wav

                    audio_info = ta.info(str(temp_audio))
                    gen_duration = audio_info.num_frames / audio_info.sample_rate
                    speed = max(0.5, min(2.0, gen_duration / duration))

                    (
                        ffmpeg
                        .input(str(temp_audio))
                        .filter("atempo", speed)
                        .output(str(dubbed_audio), acodec="pcm_s16le", ar="44100", t=duration)
                        .run(overwrite_output=True, quiet=True)
                    )

                    if temp_audio.exists():

                        temp_audio.unlink()
                    
                    success = True

                except Exception:

                    if attempts == 3:

                        warn(f"Failed to process segment {index} after 3 attempts.")
                        return False
                    
                    time.sleep(1)
                    flush()

            self.update(0.4 + (index / segments_count) * 0.2)

        del chatterbox_model, translator
        flush()

        return True

    def inference(self):

        segments_count = len(self.segments_list)
        python_venv = latentsync_path / "latentsync_venv" / "Scripts" / "python.exe"

        for index in range(1, segments_count + 1):

            video_segment = video_segments / f"video_{index}.mp4"
            audio_segment = dubbed_segments / f"dubbed_audio-{index}.wav"
            output_video = dubbed_videos / f"dubbed_video-{index}.mp4"

            if video_segment.exists() and audio_segment.exists():

                inference_args = [

                    "-m", "scripts.inference",
                    "--unet_config_path", "configs/unet/stage2_efficient.yaml",
                    "--inference_ckpt_path", "checkpoints/latentsync_unet.pt",
                    "--inference_steps", "20",
                    "--guidance_scale", "1.5",
                    "--enable_deepcache",
                    "--video_path", str(video_segment),
                    "--audio_path", str(audio_segment),
                    "--video_out_path", str(output_video),
                    
                    ]

                try:

                    subprocess.run([str(python_venv)] + inference_args, cwd=str(latentsync_path))

                except Exception:

                    warn(f"An error occurred during the inference of segment {index} !")

                self.update(0.65 + (index / segments_count) * 0.3)

    def concatenate(self):

        dubbed_files = sorted(list(dubbed_videos.glob("dubbed_video-*.mp4")), key=lambda x: int(x.stem.split('-')[1]))

        if dubbed_files:

            with open(concat_file, "w") as concatenation:

                for dubbed_video in dubbed_files:

                    concatenation.write("file " + shlex.quote(str(dubbed_video.absolute())) + "\n")

            final_video = script_path / "dubbed.mp4"

            try:

                (
                    ffmpeg
                    .input(str(concat_file), format="concat", safe=0)
                    .output(
                        str(final_video),
                        vcodec="libx264",
                        preset="fast",
                        crf=19,
                        movflags="+faststart",
                        pix_fmt="yuv420p",
                        acodec="aac",
                        audio_bitrate="320k"
                    )
                    
                    .run(overwrite_output=True, quiet=True)
                )

            except Exception:

                warn("An error occurred while concatenating the dubbed video segments !")

            if final_video.exists():

                info("Your video has just been dubbed !")

                for directory_path in deleted_dirs:

                    if directory_path.exists():
                        
                        shutil.rmtree(directory_path)
                    
                if concat_file.exists():

                    concat_file.unlink()

def processing(source_video, language, progression):

    dubbing = Dubbing(source_video, language, progression)

    try:

        dubbing.update(0.05)
        dubbing.extract_audio()
        
        if not (ffmpeg_path / "ffmpeg.wav").exists():

            warn("The audio could not be extracted from the video !")
            return

        dubbing.update(0.1)
        dubbing.separate_vocals()
        
        if not demucs_wav.exists():

            warn("Demucs was unable to isolate the voice from the sound effects !")
            return

        dubbing.update(0.25)
        dubbing.detect_language()

        dubbing.update(0.3)
        dubbing.transcribe_audio()

        dubbing.update(0.4)
        chatterbox_model, translator = dubbing.prepare_tts()

        if not dubbing.process_segments(chatterbox_model, translator):

            warn("An error occurred during the translation or TTS generation of an audio segment !")
            return

        dubbing.update(0.65)
        dubbing.inference()

        dubbing.update(0.95)
        dubbing.concatenate()

        dubbing.update(1.0)
        
    except torch.cuda.OutOfMemoryError:

        warn("Your video could not be processed due to insufficient VRAM memory !")

    finally:

        flush()