import subprocess
import os

path_dirname = os.path.dirname
path_abspath = os.path.abspath

current_file = path_abspath(__file__)
script_directory   = path_dirname(current_file)

def requirements():

    packages = [

        "chatterbox-tts",
        "customtkinter",
        "deep-translator",
        "ffmpeg-python",
        "GitPython",
        "huggingface_hub==0.23.4",
        "numpy",
        "pyftpdlib",
        "python-vlc",
        "torch",
        "torchvision",
        "torchaudio",
        "wget"

        ]

    index = [
    
        "--index-url", "https://download.pytorch.org/whl/cu121",
        
        ]

    result = subprocess.run(

        ["pip", "install", *packages, *index],
        capture_output=True,
        text=True,
        encoding="utf-8"
        
        )

    print(result.stdout)
    input("Press any key to exit.")
    
if __name__ == "__main__":

    requirements()