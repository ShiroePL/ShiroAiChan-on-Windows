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


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")

windll.shcore.SetProcessDpiAwareness(1) #make window sharp on high dpi screens

# Initialize the question to speech engine 
engine=pyttsx3.init()
conn = None
api = None
global stop_listening_flag
stop_listening_flag = False
global recording_key
recording_key = False
default_user = "normal"
font_family = "Baloo Bhai 2 SemiBold"
answer_history = [] #for the history of answers

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




def transcribe_audio_question(filename):
    start_time = time.time()
    # Load audio file as base64 encoded string
    with open(f"./kiki_hub/{filename}.wav", "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode("utf-8")

    response = requests.post("http://127.0.0.1:7860/run/predict", json={
        "data": [
            "transcribe",
            "gpu",
            "en",
            "base.en",
            {"name": "{filename}.wav", "data": f"data:audio/wav;base64,{audio_data}"},
            {"name": "{filename}.wav", "data": f"data:audio/wav;base64,{audio_data}"}
        ]
    }).json()

    question = response["data"][0]
    print("-------") 
    print("question from audio question: " + question)
    end_time = time.time()
    print("time elapsed on transcription: " + str(end_time - start_time))
    print("-------")
    return question



def play_audio_fn(filename):
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(f'./kiki_hub/{filename}.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print("Playing voice")
    except:
        print("Error or ended reading audio.")
    finally:
        pygame.mixer.quit()


def print_response_label(response):
    response_widget.delete('1.0', 'end')
    response_widget.insert(tk.END, f"{response}", 'center')
    response_widget.tag_configure('center', justify='center')
    response_widget.insert(tk.END, "\n")
   
def print_log_label(response):
    log_label.config(text=response)




# ----------- START FUNCTIONS FOR THE arrows

def add_answer_to_history(answer):
    answer_history.append(answer)

current_answer_index = -1

def show_previous_answer():
    global current_answer_index
    if current_answer_index > 0:
        current_answer_index -= 1
        display_answer(answer_history[current_answer_index])

def show_next_answer():
    global current_answer_index
    if current_answer_index < len(answer_history) - 1:
        current_answer_index += 1
        display_answer(answer_history[current_answer_index])


def display_answer(answer):
    # Update your GUI element (e.g., a Label) that displays the answer
    print_response_label(answer)

# ----------- END FUNCTIONS FOR THE arrows

def on_ctrl_press(event):
    global recording_key
    if not recording_key:
        start_voice_control()
        recording_key = True
    else:
        stop_listening()
        recording_key = False


def display_messages_from_database_only(messages):
    show_history_from_db_widget.delete('1.0', 'end')
    for message in messages:
        role = message['role']
        content = message['content']
        show_history_from_db_widget.insert(tk.END, f"Role: {role}\n", 'center')
        show_history_from_db_widget.tag_configure('center', justify='center')
        show_history_from_db_widget.insert(tk.END, f"{content}\n\n", 'center')
        
    show_history_from_db_widget.see('end')



def voice_control(input_text=None):
    global stop_listening_flag
    global running
    stop_listening_flag = False
    global current_answer_index

    name = table_name_input.get()  # takes name from input

    choice = mute_or_unmute.get()
    print("Your name?: " + name)
    print("Do you want voice? You chose: " + choice)
    print("say 'exit program' to exit the program")


    connect_to_phpmyadmin.check_user_in_database(name)
    recognizer = sr.Recognizer()

    
    while running:  # while running is true

        messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)

        if input_text is None:
            update_progress_bar(10), print_log_label("recording...")
            print("started listening")
            beep = "cute_beep"  # started recording
            play_audio_fn(beep)

            print("Started recording: say you question NOW")

            question_file = "question"
            filename = f"./kiki_hub/{question_file}.wav"

            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                source.pause_threshold = 1

                audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)

                if stop_listening_flag:
                    print("Stopped recording on user request via clicking button")
                    print("---------------------------------")
                    update_progress_bar(0), print_log_label("stopped rec. test raz dwa trzy cztery")
                    beep = "cute_beep"  # NEEEEEEEEEEEEEEESD TO FIND ANOTHER SOUND
                    play_audio_fn(beep)
                    break
                with open(filename, "wb") as f:
                    f.write(audio.get_wav_data())
                f.close()

                update_progress_bar(20), print_log_label("transcribing...")  # recorded audio

                try:
                    print("---------------------------------")

                    question = transcribe_audio_question(question_file)
                except Exception as e:
                    print("An error occurred: {}".format(e))
        else:
            question = input_text
            input_text = None

        # The rest of the code remains the same

        cleaned_question = question.translate(str.maketrans("", "", string.punctuation)).strip().lower()

        if profanity.contains_profanity(question) == True:  # dcensor question words for openAI send
            question = profanity.censor(answer)

        if question:

            if input_text is None:
                update_progress_bar(30), print_log_label("transcribed.")
            else:
                update_progress_bar(30), print_log_label("question given in input.")


            if cleaned_question in ("bye bye shiro", "exit program", "bye bye shira"):
                beep = "cute_beep"  # NEEEEEEEEEEEEEEESD TO FIND ANOTHER SOUND
                play_audio_fn(beep)
                sys.exit()
            else:
                # to database
                question = f"Madrus: {question}"
                print("question variable:" + question)
                messages.append({"role": "user", "content": question})
                
                    # send to open ai for answer
                update_progress_bar(40), print_log_label("sending to openAI...")  
                print("messages: " + str(messages))
                answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages) 
                print_response_label(answer)
                    # FOR ARROWS TO PREVIOUS ANSWERS
                add_answer_to_history(answer)
                current_answer_index = len(answer_history) - 1
                    # END OF ARROWS TO PREVIOUS ANSWERS
                update_progress_bar(60), print_log_label("got answer") 

                if choice == "Yes": #IF YES THEN WITH VOICE
                    request_voice.request_voice_fn(answer) #request Azure TTS to for answer
                    update_progress_bar(70), print_log_label("got voice")
                    play_audio_fn("response")
                    

                print("ShiroAi-chan: " + answer)
                
                
                if profanity.contains_profanity(answer) == True:
                    answer = profanity.censor(answer)                    
                update_progress_bar(80), print_log_label("saving to DB...")
                connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
                connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
                connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                print("---------------------------------")

                beep = "cute_beep" #END OF ANSWER
                play_audio_fn(beep)

                    #show history in text widget
                update_progress_bar(90), print_log_label("showing in text box...")
                #show_history_from_db_widget.delete('1.0', 'end')
                display_messages_from_database_only(take_history_from_database())
                

                running = False
                update_progress_bar(100), print_log_label("saved to DB, done")
                        
    
                    
        

           
    # Replace `print()` statements with `print_response()`
            # ...



def start_voice_control():
    global running
    running = True #will start the while loop in voice control
    voice_thread = threading.Thread(target=voice_control)
    voice_thread.start()

def start_voice_control_input(text):
    global running
    running = True #will start the while loop in voice control
    voice_thread = threading.Thread(target=voice_control, args=(text,))
    voice_thread.start()    


def stop_listening():
    global running
    global stop_listening_flag
    stop_listening_flag = True
    running = False #will cut off the while loop in voice control

    

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def on_closing():
    if api:
        api.close()
    root.destroy()

def update_progress_bar(value):
    filled_width = int(value * progress_width / 100)
    filled_image_cropped = filled_image.crop((0, 0, filled_width, progress_height))
    filled_photo = ImageTk.PhotoImage(filled_image_cropped)
    canvas.itemconfig(filled_progress, image=filled_photo)
    canvas.image = filled_photo  # Keep a reference to the image object to prevent garbage collection

def connect_to_vtube():
    global api
    api = VTubeStudioAPI()
    
def disconnect_from_vtube():
    global api
    api.close()

def take_history_from_database():
    name = table_name_input.get()
    connect_to_phpmyadmin.check_user_in_database(name)
    history_from_database = connect_to_phpmyadmin.only_conversation_history_from_database(name)
    return history_from_database

def display_all_descriptions():
    """Display all descriptions from the 'all_descriptions' table in a Tkinter window"""
    
    # Retrieve all descriptions from the 'all_descriptions' table
    descriptions = connect_to_phpmyadmin.get_all_descriptions()
    response_widget.delete('1.0', 'end')
    # Display the descriptions in the Text widget
    for description in descriptions:
        response_widget.insert(tk.END, f"{description['id']}: {description['description']}\n")
        response_widget.insert(tk.END, "\n")









# Display the messages in the Text widget
display_messages_from_database_only(take_history_from_database())





running = False
thread_running = False




