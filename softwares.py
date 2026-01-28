from pathlib import Path
from information import info
from warning import warn
from error import error

import os
import shutil
import wget
import subprocess
import webbrowser

path_join    = lambda *args: str(Path(*args))
path_exists  = lambda path: Path(path).exists()
path_dirname = lambda path: str(Path(path).parent)
path_abspath = lambda path: str(Path(path).resolve())

current_file = path_abspath(__file__)
script_directory   = path_dirname(current_file)

software_directory = path_join(script_directory, "software")
visual_directory = path_join(script_directory, "vs_BuildTools.exe")


class Software:

    class Verification:

        @staticmethod
        def winget():

                info("Winget must be installed on your computer to download all the software that DubSync needs to function properly !")

                winget_url = "https://aka.ms/getwingetpreview"

                winget_directory = path_join(software_directory, "winget")
                winget_bundle = path_join(winget_directory, "winget.msixbundle")

                for download_directory in [software_directory, winget_directory]:

                    if not path_exists(download_directory):

                        os.makedirs(download_directory)
                        
                try:

                    wget.download(winget_url, out=winget_bundle)

                    if path_exists(winget_bundle):

                        winget_succes = (

                            "Winget has just been downloaded.\n"
                            "Please proceed with the installation by following the instructions."
                        
                            )

                        info(winget_succes)

                        subprocess.run([
                            
                            "powershell", 
                            "-Command", 
                            f"Start-Process '{winget_bundle}'"
                            
                            ])

                    else:

                        warn("Winget could not be downloaded !")

                except Exception:

                    error("An error occurred while attempting to download Winget !")

        @staticmethod
        def git():

                info("Git must be installed on your computer to download LatentSync !")
                
                git_install = subprocess.run([
                    
                    "winget", 
                    "install", 
                    "--id", 
                    "Git.Git", 
                    "-e", 
                    "--accept-source-agreements", 
                    "--accept-package-agreements"
                    
                    ])
                
                if git_install.returncode == 0:
                    
                    info("Git has just been installed on your computer.")

                else:
                    
                    error("Git could not be installed on your computer !")

        @staticmethod
        def visual():

            if not path_exists(path_join(script_directory, "vs_BuildTools.exe")):

                info("To ensure lip synchronization, DubSync relies on LatentSync, which requires downloading the Desktop C++ development pack via Visual Studio Build Tools !")

                visual_url = "https://download.visualstudio.microsoft.com/download/pr/98009c04-e4b8-4223-8794-58f961de75a4/b7a70e4acdf18aaaba4e13e17c7c157a12d6512458d60d5c2001a373741329cb/vs_BuildTools.exe"
                wget.download(visual_url, visual_directory)

                os.system("cls")

                if path_exists(visual_directory):

                    info("Visual Studio Build Tools has just been downloaded ; please install the C++ desktop development pack !")
                    subprocess.run([visual_directory])

                else:

                    error("An error occurred while downloading Visual Studio Build Tools !")
                    webbrowser.open(visual_url)

        @staticmethod
        def latentsync():
          
            from git import Repo

            latentsync_url = "https://github.com/bytedance/LatentSync.git"
            
            models_url = "https://huggingface.co/ByteDance/LatentSync-1.5"
            checkpoints_directory = path_join(latentsync_directory, "checkpoints")

            info("LatentSync must be downloaded in order to perform lip synchronization !")

            try:

                Repo.clone_from(latentsync_url, latentsync_directory)

                if path_exists(latentsync_directory):

                    info("LatentSync has just been downloaded to work properly, all necessary components must now be downloaded !")

                    try:
                            
                        if not path_exists(checkpoints_directory):

                            os.makedirs(checkpoints_directory)

                        Repo.clone_from(models_url, checkpoints_directory)

                        latentsync_venv = path_join(latentsync_directory, "latentsync_venv")
                        python_venv = path_join(latentsync_venv, "Scripts", "python.exe")

                        if not path_exists(python_venv):

                            venv_command = f'py -3.11 -m venv "{latentsync_venv}"'
                            venv_directory = subprocess.run(venv_command, cwd=latentsync_directory, shell=True)

                            if venv_directory.returncode == 0:

                                install_requirements = subprocess.run(

                                    f'"{python_venv}" -m pip install -r requirements.txt',
                                    cwd=latentsync_directory,
                                    shell=True
                                    
                                    )
                                    
                                os.system("cls")

                                if install_requirements.returncode == 0:

                                    info("All LatentSync dependencies have just been downloaded !")

                                else:

                                    warn("Not all LatentSync dependencies could be downloaded !")

                    except Exception:

                        error("An error occurred while attempting to download the LatentSync templates !")

                else:

                    warn("LatentSync could not be downloaded !")

            except Exception:

                error("An error occurred while attempting to download LatentSync !")

        @staticmethod
        def ffmpeg():

                info("FFmpeg must be installed on your computer to extract the audio track from your videos !")
                
                ffmpeg_install = subprocess.run([
                    
                    "winget", 
                    "install", 
                    "--id", 
                    "Gyan.FFmpeg", 
                    "-e",
                    "--accept-source-agreements",
                    "--accept-package-agreements"

                    ])
                
                if ffmpeg_install.returncode == 0:
                    
                    info("FFmpeg has just been installed on your computer !")

                else:
                    
                    error("FFmpeg could not be installed on your computer !")

        @staticmethod
        def vlc():
                
                info("VLC must be installed on your computer to view your videos !")
                
                vlc_install = subprocess.run([

                    "winget",                       
                    "install", 
                    "--id", 
                    "VideoLAN.VLC", 
                    "-e",
                    "--accept-source-agreements",
                    "--accept-package-agreements"
                    
                    ])
                
                if vlc_install.returncode == 0:
                    
                    info("VLC has just been installed on your computer !")

                else:
                    
                    error("VLC could not be installed on your computer !")


if __name__ == "__main__":

    latentsync_directory = path_join(script_directory, "LatentSync")
    
    ffmpeg_path = b"FFmpeg" in subprocess.run([

        "winget", 
        "list", 
        "--id", 
        "Gyan.FFmpeg"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE).stdout
    
    vlc_path = b"VLC" in subprocess.run([

        "winget", 
        "list", 
        "--id", 
        "VideoLAN.VLC"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE).stdout

    softwares = {

        "winget": (shutil.which("winget.exe"), Software.Verification.winget),
        "git": (shutil.which("git.exe"), Software.Verification.git),
        "visual": (path_exists(visual_directory), Software.Verification.visual),
        "latentsync": (path_exists(latentsync_directory), Software.Verification.latentsync),
        "ffmpeg": (ffmpeg_path, Software.Verification.ffmpeg),
        "vlc": (vlc_path, Software.Verification.vlc)

        }

    if all(software[0] for software in softwares.values()):

        info("You have all the software that DubSync needs to function !")
    
    else:

        for software in softwares.values():

            if not software[0]:

                software[1]()