import threading
# Add your other imports here
# ...
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyttsx3
import time 
import kiki_hub.request_whisper as request_whisper
import base64
import requests
import wave
import pyaudio
import connect_to_phpmyadmin
import time
from better_profanity import profanity
import chatgpt_api
import request_voice_tts as request_voice
import sys
from db_config import conn
from tkinter import scrolledtext
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
from pathlib import Path
from ctypes import windll
from vtube_studio_api import VTubeStudioAPI
from PIL import Image, ImageTk
import string
import keyboard
from tkinter.font import Font
import pygame
from on_key_shirochan_gui import *


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="black", foreground="#7FD5EA", relief="solid", borderwidth=2, font=("Inter Bold", 9))
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def create_gui():
    
    # GUI elements
    root = tk.Tk()
    root.title("ShiroAi-chan Control Panel")



    root.geometry("1200x800")
    root.configure(bg = "#4B98E0")

    canvas = Canvas(
        root,
        bg = "#4B98E0",
        height = 800,
        width = 1200,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)


    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        600.0,
        400.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=relative_to_assets("image_2.png"))
    image_2 = canvas.create_image(
        959.0,
        400.0,
        image=image_image_2
    )




    canvas.create_text(
        284.0,
        10.0,
        anchor="nw",
        text="ShiroAi-chan Control Panel",
        fill="#78CBED",
        font=(font_family, 53 * -1)
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=start_voice_control,
        relief="flat"
    )
    button_1.place(
        x=39.0,
        y=89.0,
        width=161.0,
        height=55.0
    )

    #tet2sss
    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=stop_listening,
        relief="flat"
    )
    button_2.place(
        x=215.0,
        y=89.0,
        width=158.0,
        height=47.0
    )

    button_image_3 = PhotoImage(
        file=relative_to_assets("button_3.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: (connect_to_phpmyadmin.reset_chat_history(table_name_input.get()), print_log_label("reset chat history")),
        relief="flat"
    )
    button_3.place(
        x=396.0,
        y=89.0,
        width=131.0,
        height=47.0
    )


    button_image_4 = PhotoImage(
        file=relative_to_assets("button_4.png"))
    button_4 = Button(
        image=button_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=connect_to_vtube,
        relief="flat"
    )
    button_4.place(
        x=39.0,
        y=158.0,
        width=157.0,
        height=47.0
    )

    button_image_5 = PhotoImage(
        file=relative_to_assets("button_5.png"))
    button_5 = Button(
        image=button_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=disconnect_from_vtube,
        relief="flat"
    )
    button_5.place(
        x=215.0,
        y=158.0,
        width=168.0,
        height=47.0
    )

    button_image_6 = PhotoImage(
        file=relative_to_assets("button_6.png"))
    button_6 = Button(
        image=button_image_6,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: api.play_animation("introduce"),
        relief="flat"
    )
    button_6.place(
        x=396.0,
        y=158.0,
        width=134.0,
        height=47.0
    )






    left_arrow_img = PhotoImage(
        file=relative_to_assets("button_7.png"))
    left_arrow = Button(
        image=left_arrow_img,
        borderwidth=0,
        highlightthickness=0,
        command=show_previous_answer,
        relief="flat"
    )
    left_arrow.place(
        x=3.0,
        y=214.0,
        width=43.0,
        height=36.0
    )

    right_arrow_img = PhotoImage(
        file=relative_to_assets("button_8.png"))
    right_arrow = Button(
        image=right_arrow_img,
        borderwidth=0,
        highlightthickness=0,
        command=show_next_answer,
        relief="flat"
    )
    right_arrow.place(
        x=51.0,
        y=214.0,
        width=43.0,
        height=36.0
    )


    button_image_9 = PhotoImage(
        file=relative_to_assets("button_9.png"))
    button_9 = Button(
        image=button_image_9,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print_response_label(connect_to_phpmyadmin.show_character_description(table_name_input.get())),
        relief="flat"
    )
    button_9.place(
        x=12.0,
        y=252.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_9, "Show persona description for current table.")

    button_image_10 = PhotoImage(
        file=relative_to_assets("button_10.png"))
    button_10 = Button(
        image=button_image_10,
        borderwidth=0,
        highlightthickness=0,
        command=display_all_descriptions,
        relief="flat"
    )
    button_10.place(
        x=9.0,
        y=314.0,
        width=45.0,
        height=42.0
    )

    tooltip = ToolTip(button_10, "Show all descriptions of persona.")


    button_image_11 = PhotoImage(
        file=relative_to_assets("button_11.png"))
    button_11 = Button(
        image=button_image_11,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: response_widget.delete('1.0', 'end'), #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        relief="flat"
    )
    button_11.place(
        x=12.0,
        y=376.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_11, "Clean text box on the right")


    button_image_12 = PhotoImage(
        file=relative_to_assets("button_12.png"))
    button_12 = Button(
        image=button_image_12,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: show_history_from_db_widget.delete('1.0', 'end'),
        relief="flat"
    )
    button_12.place(
        x=166.0,
        y=536.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_12, "Clean text box below.")


    button_image_13 = PhotoImage(
        file=relative_to_assets("button_13.png"))
    button_13 = Button(
        image=button_image_13,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: connect_to_phpmyadmin.update_character_description(table_name_input.get() ,show_history_from_db_widget.get("1.0", tk.END)),
        relief="flat"
    )
    button_13.place(
        x=228.0,
        y=536.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_13, "Insert new description to current table.")


    button_image_14 = PhotoImage(
        file=relative_to_assets("button_14.png"))
    button_14 = Button(
        image=button_image_14,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: display_messages_from_database_only(take_history_from_database()),
        relief="flat"
    )
    button_14.place(
        x=290.0,
        y=536.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_14, "Show history of chat in current table.")

    button_image_15 = PhotoImage(
        file=relative_to_assets("button_15.png"))
    button_15 = Button(
        image=button_image_15,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: start_voice_control_input(show_history_from_db_widget.get("1.0", tk.END)),
        relief="flat"
    )
    button_15.place(
        x=352.0,
        y=536.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_15, "Send text message to Shiro")

    button_image_16 = PhotoImage(
        file=relative_to_assets("button_16.png"))
    button_16 = Button(
        image=button_image_16,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("doesnt work for now"),
        relief="flat"
    )
    button_16.place(
        x=12.0,
        y=438.0,
        width=42.0,
        height=42.0
    )

    tooltip = ToolTip(button_16, "Stop Shiro from talking. now doesnt work")

    entry_image_1 = PhotoImage(
        file=relative_to_assets("entry_1.png"))
    entry_bg_1 = canvas.create_image(
        100.0,
        52.0,
        image=entry_image_1
    )


    image_image_5 = PhotoImage(
        file=relative_to_assets("image_5.png"))
    image_5 = canvas.create_image(
        540.0,
        252.0,
        image=image_image_5
    )

    table_name_input = Entry(
        bd=0,
        bg="#A8E1F6",
        fg="#000716",
        highlightthickness=0,
        justify="center",
    )
    table_name_input.place(
        x=55.0,
        y=37.8,
        width=90.0,
        height=27.0,
    )

    table_name_input.insert(0, default_user)

    canvas.create_text(
        50.0,
        12.0,
        anchor="nw",
        text="Your name:",
        fill="#A8E1F6",
        font=(font_family, 20 * -1)
    )
    #OMG RADIO BUTTONS START--------------------------------------------------------------------------------------------------
    # Create the Radiobutton widgets
    style = ttk.Style()
    # Configure the custom radio button style
    style.layout("Custom.TRadiobutton", [
        ("Custom.TRadiobutton.focus", {"children":
            [("Custom.TRadiobutton.indicator", {"side": "left", "sticky": ""}),
            ("Custom.TRadiobutton.padding", {"expand": "1", "sticky": "nswe", "children":
                [("Custom.TRadiobutton.label", {"sticky": "nswe"})]
            })
            ]
        })
    ])

    style.configure("Custom.TRadiobutton", background="#000000", foreground="#FFFFFF", font=(font_family, 12))
    style.map("Custom.TRadiobutton", background=[("active", "#000000")])

    # Create custom images for the radio button states
    normal_image = tk.PhotoImage(file=relative_to_assets("black.png"))
    selected_image = tk.PhotoImage(file=relative_to_assets("check.png"))



    style.element_create("Custom.TRadiobutton.indicator", "image", normal_image,
                        ("selected", selected_image),
                        sticky="", padding=2)


    mute_or_unmute = tk.StringVar()
    mute_or_unmute.set("Yes")
    mute_or_unmute_yes = ttk.Radiobutton(root, text=" voice", variable=mute_or_unmute, value="Yes", style="Custom.TRadiobutton")
    mute_or_unmute_no = ttk.Radiobutton(root, text=" no voice", variable=mute_or_unmute, value="No", style="Custom.TRadiobutton")
    mute_or_unmute_yes.place(x=169, y=17)
    mute_or_unmute_no.place(x=169, y=50)

    #OMG RADIO BUTTONS ENDDD--------------------------------------------------------------------------------------------------



    # PROGRESS BARRRRRRRRRRRRRRRRRRRR OMGGGGGGGGGGGGGGG
    background_image = Image.open("./assets/frame0/image_3.png")
    filled_image = Image.open("./assets/frame0/image_4.png")

    progress_width, progress_height = background_image.size

    background_photo = ImageTk.PhotoImage(background_image)

    canvas = tk.Canvas(root, width=progress_width, height=progress_height,bg="black", highlightthickness=0, bd=0, relief='ridge')
    canvas.place(x=543, y=136)

    background_progress = canvas.create_image(0, 0, anchor=tk.NW, image=background_photo)
    filled_progress = canvas.create_image(0, 0, anchor=tk.NW)
    # END PROGRESS BARRRRRRRRRRRRRRRRRRRR OMGGGGGGGGGGGGGGG



    response_widget = tk.Text(root, wrap=tk.WORD, padx=10, pady=10, width=40, height=10,
                        bg='black', fg='#A8E1F6', font=(font_family, 14),  bd=0)
    response_widget.place(x=66, y=252, width=428, height=226)


                # i think i will change this to show_history_from_db_widget
    log_label = tk.Label(
        root,
        text="",
        bg="black",
        fg="#A8E1F6",
        font=(font_family, 12 * -1),
        wraplength=110,
        anchor="center",  # Centers the text vertically
        justify="center",  # Centers the text horizontally
        width=17,  # Adjust this value to control the width of the label
    )
    log_label.place(
        x=543,
        y=158,
    )

    # Create the Text widget
    show_history_from_db_widget = tk.Text(root, wrap=tk.WORD, padx=10, pady=10, width=40, height=10,
                        bg='black', fg='#78CBED', font=(font_family, 9),  bd=0)
    show_history_from_db_widget.place(x=66, y=587, width=428, height=198)
    show_history_from_db_widget.see('end')


    # Display the messages in the Text widget
    display_messages_from_database_only(take_history_from_database())

    show_history_from_db_widget.see('end')


    update_progress_bar(100)
    root.resizable(False, False)
    
    













    return root