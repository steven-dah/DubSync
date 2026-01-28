from pathlib import Path
from PIL import Image
from warning import warn
from information import info
from tkinter import filedialog
from dubbing import processing

import requests
import sys
import customtkinter as ctk
import vlc
import ftplib
import threading

current_file = Path(__file__).resolve()
script_directory = current_file.parent

icons_directory = script_directory / "icons"

ICONS = {}

for icon in icons_directory.iterdir():

    if icon.suffix == ".png":

        icon_name = icon.stem
        icon_path = icon

        ICONS[icon_name] = ctk.CTkImage(

            light_image=Image.open(icon_path),
            dark_image=Image.open(icon_path),
            size=(24, 24)

            )

class DubSync:
    
    def __init__(self):
        
        self.dubsync_title = "DubSync :"

        self.dubsync = ctk.CTk()
        self.dubsync.title(self.dubsync_title)
        self.dubsync.geometry("810x1000")
        self.dubsync.resizable(False, False)

        self.ftp_window = None

        ctk.set_appearance_mode("lightgray")
        self.calibri_bold = ctk.CTkFont("Calibri", 15, "bold")

        self.vlc_instance = vlc.Instance("--avcodec-hw=none", "--quiet")
        self.video_player = self.vlc_instance.media_player_new()
        self.video_path = None

        self.language_var = ctk.StringVar(value="lang")
        
        self.supported_languages = {

            "da": "da",
            "de": "de",
            "el": "el",
            "en": "en",
            "es": "es",
            "fi": "fi",
            "fr": "fr",
            "he": "he",
            "hi": "hi",
            "it": "it",
            "ja": "ja",
            "ko": "ko",
            "ms": "ms",
            "nl": "nl",
            "no": "no",
            "pl": "pl",
            "pt": "pt",
            "ru": "ru",
            "sv": "sv",
            "sw": "sw",
            "zh": "zh",

            }

        functions_list = [

            "top_frame",
            "video_frame",
            "languages_frame",
            "select_button",
            "play_button",
            "pause_button",
            "processing_button",
            "rewind_button",
            "forward_button",
            "information_label"

        ]

        for function_name in functions_list:

            getattr(self, function_name)()

    def top_frame(self):

        self.top_frame = ctk.CTkFrame(

            self.dubsync,
            height=45,
            width=800,
            fg_color="#1E1E1E",

            )

        self.top_frame.place(x=0, y=0, relwidth=1)

        self.ftp_button = ctk.CTkButton(

            self.top_frame,
            text="",
            image=ICONS.get("ftp"),
            width=80,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#242424",
            corner_radius=5,
            command=self.ftp

            )

        self.ftp_button.place(x=5, y=5)

        self.progress_bar = ctk.CTkProgressBar(

            self.top_frame,
            width=700, 
            height=10,
            corner_radius=10,
            progress_color="#FFD700"
            
            )

        self.progress_bar.place(x=95, y=15)
        self.progress_bar.set(0)

    def video_frame(self):

        self.video_frame = ctk.CTkFrame(

            self.dubsync, 
            height=400, 
            width=800,
            fg_color="black",
            corner_radius=0

            )

        self.video_frame.place(x=5, y=50)

    def languages_frame(self):

        self.languages_frame = ctk.CTkFrame(

            self.dubsync, 
            height=350, 
            width=530, 
            corner_radius=20,
            fg_color="#242424"

            )

        self.languages_frame.place(x=3, y=455)

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns  

        self.language_buttons = []

        for index, lang in enumerate(self.supported_languages.keys()):
            
            row = index // columns
            col = index % columns

            buttons = ctk.CTkButton(

                self.languages_frame,
                text="",
                image=ICONS.get(lang),
                height=50,
                width=buttons_width,
                corner_radius=15,
                hover_color="#708090",
                border_color="#555555",
                border_width=2,
                fg_color="#242424",
                command=lambda l=lang: self.select_language(l)

                )

            buttons.grid(

                row=row, 
                column=col, 
                padx=5,         
                pady=4,
                sticky="nsew"
                
                )

            self.language_buttons.append(buttons)

    def select_button(self):

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns

        self.select_button = ctk.CTkButton(

            self.dubsync, 
            text="Select a video.", 
            image=ICONS.get("select"),
            height=50, 
            width=buttons_width,
            corner_radius=15,
            hover_color="#43A047",
            border_color="#555555",
            border_width=2,
            fg_color="#2E7D32",
            font=self.calibri_bold, 
            command=self.select_video

            )

        self.select_button.place(x=10, y=865)

    def play_button(self):

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns

        self.play_button = ctk.CTkButton(
            
            self.dubsync, 
            text="", 
            image=ICONS.get("play"),
            height=50,
            width=buttons_width, 
            corner_radius=15,
            hover_color="#708090",
            border_color="#555555",
            border_width=2,
            fg_color="#242424",
            command=self.play

            )

        self.play_button.place(x=275, y=865)

    def pause_button(self):

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns

        self.pause_button = ctk.CTkButton(

            self.dubsync, 
            text="", 
            image=ICONS.get("pause"),
            width=buttons_width, 
            height=50, 
            corner_radius=15,
            hover_color="#708090",
            border_color="#555555",
            border_width=2,
            fg_color="#242424",
            command=self.pause

            )

        self.pause_button.place(x=540, y=865)

    def processing_button(self):

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns

        self.processing_button = ctk.CTkButton(

            self.dubsync, 
            text="Perform the treatment.", 
            image=ICONS.get("process"),
            height=50, 
            width=buttons_width, 
            corner_radius=15,
            hover_color="#E53935",
            border_color="#555555",
            border_width=2,
            fg_color="#C62828",
            font=self.calibri_bold,
            command=self.dubbing

            )

        self.processing_button.place(x=10, y=923)

    def rewind_button(self):

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns

        self.rewind_button = ctk.CTkButton(

            self.dubsync, 
            text="", 
            image=ICONS.get("rewind"),
            width=buttons_width, 
            height=50, 
            corner_radius=15,
            hover_color="#708090",
            border_color="#555555",
            border_width=2,
            fg_color="#242424",
            command=self.rewind

            )

        self.rewind_button.place(x=275, y=923)

    def forward_button(self):

        columns = 3
        buttons_width = (795 - (columns - 1) * 10) // columns

        self.forward_button = ctk.CTkButton(

            self.dubsync, 
            text="", 
            image=ICONS.get("forward"),
            width=buttons_width, 
            height=50, 
            corner_radius=15,
            hover_color="#708090",
            border_color="#555555",
            border_width=2,
            fg_color="#242424",
            command=self.forward

            )

        self.forward_button.place(x=540, y=923)

    def information_label(self):

        self.information_label = ctk.CTkLabel(

            self.dubsync,
            text="Developped by Steven DAHMS-DUC - All rights reserved.",
            text_color="white",
            font=self.calibri_bold,

            )

        self.information_label.place(x=15, y=975)

    def play(self):

        self.video_player.play()

    def pause(self):

        self.video_player.pause()

    def rewind(self):

        self.video_player.set_time(max(0, self.video_player.get_time() - 5000))

    def forward(self):

        self.video_player.set_time(self.video_player.get_time() + 5000)

    def ftp(self):

        if self.ftp_window is None or not self.ftp_window.winfo_exists():

            self.ftp_window = ctk.CTkToplevel(self.dubsync)
            self.ftp_window.title("DubSync - FTP :")

            self.ftp_window.geometry("300x250")
            self.ftp_window.resizable(False, False)
            self.ftp_window.withdraw()

            blue = "#3B8ED0"

            ip_label = ctk.CTkLabel(
                
                self.ftp_window,
                text="IP address : ",
                font=self.calibri_bold,
                corner_radius=5,
                fg_color=blue

                )

            ip_label.place(x=10, y=10, anchor="nw")

            ip_entry = ctk.CTkEntry(

                self.ftp_window,
                placeholder_text="192.168.1.254",
                text_color="white",
                width=100

                )

            ip_entry.place(x=105, y=10)

            port_label = ctk.CTkLabel(
                
                self.ftp_window,
                text="Port :",
                font=self.calibri_bold,
                corner_radius=5,
                fg_color=blue

                )

            port_label.place(x=10, y=50, anchor="nw")

            port_entry = ctk.CTkEntry(

                self.ftp_window,
                text_color="white",
                placeholder_text="21",
                width=50

                )

            port_entry.place(x=65, y=50)

            user_label = ctk.CTkLabel(
                
                self.ftp_window,
                text="Username :",
                font=self.calibri_bold,
                corner_radius=5,
                fg_color=blue

                )

            user_label.place(x=10, y=90, anchor="nw")

            user_entry = ctk.CTkEntry(

                self.ftp_window,
                text_color="white",
                placeholder_text="DubSync",
                width=100

                )

            user_entry.place(x=100, y=90)

            password_label = ctk.CTkLabel(
                
                self.ftp_window,
                text="Password :",
                font=self.calibri_bold,
                corner_radius=5,
                fg_color=blue

                )

            password_label.place(x=10, y=130, anchor="nw")

            password_entry = ctk.CTkEntry(

                self.ftp_window,
                text_color="white",
                placeholder_text="DubSync@2025",
                width=120,
                show="*"

                )

            password_entry.place(x=100, y=130)

            destination_label = ctk.CTkLabel(
                
                self.ftp_window,
                text="Destination directory :",
                font=self.calibri_bold,
                corner_radius=5,
                fg_color=blue

                )

            destination_label.place(x=10, y=170, anchor="nw")

            destination_entry = ctk.CTkEntry(

                self.ftp_window,
                text_color="white",
                placeholder_text="DubSync/Dubbed",
                width=120

                )

            destination_entry.place(x=170, y=170)

            def upload():

                username = user_entry.get()
                password = password_entry.get()
                ftp_server = ip_entry.get()
                
                port_value = port_entry.get()
                port = int(port_value) if port_value else 21

                video_upload = script_directory / "dubbed.mp4"

                if not video_upload.exists():
                
                    video_info = "Please process your video before uploading it to the FTP server."
                    warn(video_info)
                    
                    return

                try:

                    with ftplib.FTP_TLS() as ftp_client:

                        ftp_client.connect(ftp_server, port)
                        ftp_client.auth()
                        ftp_client.login(username, password)
                        ftp_client.prot_p()
                        ftp_client.set_pasv(True)

                        ftp_client.cwd(destination_entry.get())

                        with open(video_upload, "rb") as file:

                            ftp_client.storbinary("STOR dubbed.mp4", file)

                        info("Your video has just been uploaded to the FTP server.")

                except ftplib.all_errors:

                    warn("An error occurred during the transfer !")

            upload_button = ctk.CTkButton(

                self.ftp_window,
                text="Upload your video to the FTP server.",
                font=self.calibri_bold,
                fg_color="#2E7D32", 
                hover_color="#43A047",
                corner_radius=20,
                command=lambda: threading.Thread(target=upload, daemon=True).start()
                
                )

            upload_button.place(x=10, y=210)
            
            self.ftp_window.after(10, self.ftp_window.deiconify)

        else:

            self.ftp_window.focus()

    def progression(self, percent):

        self.progress_bar.set(percent)

    def select_video(self):

        selected_file = filedialog.askopenfilename(filetypes=[("MP4", "*.mp4")])

        if not selected_file:

            return
        
        self.video_path = Path(selected_file).resolve()

        media = self.vlc_instance.media_new(self.video_path)

        self.video_player.set_media(media)
        self.video_player.set_hwnd(self.video_frame.winfo_id())

        self.video_player.play()

    def dubbing(self):

        if self.video_path is None and self.language_var.get() == "lang":

            prerequisites_info = "Please select a video and a language before you want to do the processing !"
            warn(prerequisites_info)
            
            return
        
        elif self.video_path is None:

            video_information = "Please select a video before you want to do the processing !"
            warn(video_information)

            return
        
        elif self.language_var.get() == "lang":
            
            language_info = "Please select a language before proceeding with the treatment !"
            warn(language_info)

            return
        
        threading.Thread(target=lambda: processing(self.video_path, self.supported_languages[self.language_var.get()], self.progression)).start()

    def select_language(self, lang):

        self.language_var.set(lang)

    def run(self):

        self.dubsync.mainloop()

if __name__ == "__main__":

    url = "https://www.google.com/"
    
    try:

        request = requests.get(url)

        if request.status_code == 200:

            dubsync_information = (

            "DubSync is multilingual video dubbing software with lip-syncing, based on open-source tools and specialized libraries.\n\n"
            "In the interests of transparency, ethics, and compliance with the General Data Protection Regulation (France), we would like to inform you that the translation of audio transcripts is carried out using Google Translate.\n\n"
            "As a result, some textual data from your videos may be processed or stored by Google for the purpose of analyzing or improving its services.\n\n"
        
            )

            info(dubsync_information)

    except:

        warn("To use DubSync, please be connected to a wired or wireless network with internet access !")
        sys.exit()

    app = DubSync()
    app.run()