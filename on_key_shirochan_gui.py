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
import anilist.anilist_api_requests as anilist_api_requests
import re
import timer
import random

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
anilist_mode = False
content_type_mode =""
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

def progress(percent: int, text: str):
    """ Update progress bar percents and text"""
    update_progress_bar(percent), print_log_label(text)


def display_messages_from_database_only(messages):
    show_history_from_db_widget.delete('1.0', 'end')
    for message in messages:
        role = message['role']
        content = message['content']
        show_history_from_db_widget.insert(tk.END, f"Role: {role}\n", 'center')
        show_history_from_db_widget.tag_configure('center', justify='center')
        show_history_from_db_widget.insert(tk.END, f"{content}\n\n", 'center')
        
    show_history_from_db_widget.see('end')

def button_show_anilist(media_type: str):
    
    global anilist_mode
    media_list, _ = anilist_api_requests.get_10_newest_entries(media_type) # i think it can be just anime_lise, 
    chapters_or_episodes = "episodes" if media_type == "anime" else "chapters"
    question = f"Madrus: I will give you list of my 10 most recent updated {media_type} from site AniList. Here is this list:{media_list}. I want you to remember this because in next question I will ask you to update {chapters_or_episodes} number of one {media_type}."
    #print("question from user:" + question)
    name = table_name_input.get()
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
    messages.append({"role": "user", "content": question})

    # send to open ai for answer !!!!!!!! I WONT SEND IT BECOUSE I ALREADY GOT IT FROM reformatting
    answer = "Okay, I will remember it, Madrus. I'm waiting for your next question. Give it to me nyaa."
    print_response_label(f"Here is your list of most recent watched {media_type}.{media_list}")

    #   FOR ARROWS TO PREVIOUS ANSWERS
    add_answer_to_history(f"Here is your list of most recent watched {media_type}.{media_list}")
    current_answer_index = len(answer_history) - 1
        # END OF ARROWS TO PREVIOUS ANSWERS
    
    tts_or_not = mute_or_unmute.get()
    if tts_or_not == "Yes": #IF YES THEN WITH VOICE
        request_voice.request_voice_fn(f"Here is your list of most recent watched {media_type}.") #request Azure TTS to for answer
        update_progress_bar(70), print_log_label("got voice")
        play_audio_fn("response")

    progress(80,"saving to DB...")
    connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
    print("---------------------------------")


    beep = "cute_beep" #END OF ANSWER
    play_audio_fn(beep)

        #show history in text widget
    progress(90,"showing in text box...")
    #show_history_from_db_widget.delete('1.0', 'end')
    display_messages_from_database_only(take_history_from_database())
    
    anilist_mode = True # entering anime list mode for next question to update anime/manga
    progress(100,"showed, done")

######################################################################## RANDOM QUESTIONS FROM SHIRO

questions = ['What is your favorite color?', 
             'What is your favorite movie?', 
             'What is your favorite food?']

timer_running = False
timer_thread = None

def ask_random_question():
    question = random.choice(questions)
    print(question)

def timer_for_random_questions(interval=10):
    while timer_running:
        ask_random_question()
        time.sleep(interval)

def start_timer(interval=10):
    global timer_running
    global timer_thread
    timer_running = True
    timer_thread = threading.Thread(target=timer_for_random_questions, args=(interval,))
    timer_thread.start()

def stop_timer():
    global timer_running
    global timer_thread
    timer_running = False
    if timer_thread is not None:
        timer_thread.join()

def on_talk_or_not_change(*args):
    if talk_or_not.get() == "Yes":
        start_timer(5)
    else:
        stop_timer()




###########################################################################

def voice_control(input_text=None):
    global stop_listening_flag
    global running
    
    stop_listening_flag = False
    global current_answer_index

    name = table_name_input.get()  # takes name from input

    tts_or_not = mute_or_unmute.get()
    random_questions_mode = talk_or_not.get() # for iniciating random questions from shiro from time to time

    print("Your name?: " + name)
    print("Do you want voice? You chose: " + tts_or_not)
    print("say 'exit program' to exit the program")


    connect_to_phpmyadmin.check_user_in_database(name)
    recognizer = sr.Recognizer()

    
    while running:  # while running is true
        global anilist_mode
        global content_type_mode
        messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
        #messages = connect_to_phpmyadmin.retrieve_chat_history_from_database("long_therm_memory")

        if input_text is None:
            progress(10,"recording...")
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
    
                    progress(0,"stopped recording")
                    beep = "cute_beep"  # NEEEEEEEEEEEEEEESD TO FIND ANOTHER SOUND
                    play_audio_fn(beep)
                    break
                with open(filename, "wb") as f:
                    f.write(audio.get_wav_data())
                f.close()
 
                progress(20,"transcribing...") # recorded audio
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

        if profanity.contains_profanity(question):
            question = profanity.censor(answer) # censor question words for openAI send

        if question:
                # check if question was asked using voice or input
            progress(30,"transcribed.") if input_text is None else progress(30,"question given in input.")
                # end if user wants to exit
            if cleaned_question in ("bye bye shiro", "exit program", "bye bye shira"):
                beep = "cute_beep"  # NEEEEEEEEEEEEEEESD TO FIND ANOTHER SOUND
                play_audio_fn(beep)
                sys.exit()

            elif cleaned_question in ("please remember this"): # THIS IS MODULE TO SEND TEXT TO LONG TERM MEMORY
                # to database
                question = f"Madrus: {question}"
                print("question from user:" + question)
                messages.append({"role": "user", "content": question})
                
                    # send to open ai for answer
                progress(40,"sending to openAI...")   
                print("messages: " + str(messages))
                answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages) 
                print_response_label(answer)
                
                    # FOR ARROWS TO PREVIOUS ANSWERS
                add_answer_to_history(answer)
                current_answer_index = len(answer_history) - 1
                    # END OF ARROWS TO PREVIOUS ANSWERS

                progress(60,"got answer")

                if tts_or_not == "Yes": #IF YES THEN WITH VOICE
                    request_voice.request_voice_fn(answer) #request Azure TTS to for answer
                    progress(70,"got voice")
                    play_audio_fn("response")
                    

                print("ShiroAi-chan: " + answer)
                
                
                if profanity.contains_profanity(answer) == True:
                    answer = profanity.censor(answer)                    
                progress(80,"saving to DB...")
                connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
                connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
                connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                print("---------------------------------")

                beep = "cute_beep" #END OF ANSWER
                play_audio_fn(beep)

                #show history in text widget
                progress(90,"showing in text box...")
                #show_history_from_db_widget.delete('1.0', 'end')
                display_messages_from_database_only(take_history_from_database())
                

                running = False  
                progress(100,"saved to DB, done")
            elif cleaned_question in ("show me my list of anime", "show me my list of manga"):

                content_type = "anime" if "watched" in cleaned_question else "manga"

                list_content, _ = anilist_api_requests.get_10_newest_entries("ANIME") if content_type == "anime" else anilist_api_requests.get_10_newest_entries("MANGA")  # assuming this method exists        
                 
                question = f"Madrus: I will give you list of my 10 most recent watched/read {content_type} from site AniList. Here is this list:{list_content}. I want you to remember this because in next question I will ask you to update episodes/chapters of one of them."
                #print("question from user:" + question)
                messages.append({"role": "user", "content": question})

                # send to open ai for answer !!!!!!!! I WONT SEND IT BECOUSE I ALREADY GOT IT FROM reformatting
                answer = "Okay, I will remember it, Madrus. I'm waiting for your next question. Give it to me nyaa."
                print_response_label(f"Here is your list of most recent anime/manga.{list_content}")

                #   FOR ARROWS TO PREVIOUS ANSWERS
                add_answer_to_history(f"Here is your list of most recent anime/manga.{list_content}")
                current_answer_index = len(answer_history) - 1
                    # END OF ARROWS TO PREVIOUS ANSWERS
                #update_progress_bar(60), print_log_label("got answer")
                progress(60,"got answer")

                if tts_or_not == "Yes": #IF YES THEN WITH VOICE
                    request_voice.request_voice_fn("Here is your list. *smile*") #request Azure TTS to for answer
                    progress(70,"got voice")
                    play_audio_fn("response")

                
                progress(80,"saving to DB...")
                connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
                print("---------------------------------")

                beep = "cute_beep" #END OF ANSWER
                play_audio_fn(beep)
                    #show history in text widget
                
                progress(90,"showing in text box...")
                #show_history_from_db_widget.delete('1.0', 'end')
                display_messages_from_database_only(take_history_from_database())
       
                content_type_mode = "anime" if "watched" in cleaned_question else "manga" # i need this so in next question i know what to update (anime or manga)
                running = False
                anilist_mode = True # entering anilist mode for next question to update anime/manga

                progress(100,"showed, done")
            elif anilist_mode: # she is in animelist mode, so she rebebmers list i gave her 
                    # make shiro find me id of anime/manga

                content_type = content_type_mode   

                end_question = "I would like you to answer me giving me ONLY THIS: ' title:<title>,id:<id>,"
                extra = " episodes:<episodes>'. Nothing more." if content_type == "anime" else " chapters:<chapters>'. Nothing more."
                question = f"Madrus: {question}. {end_question}{extra}"

                #print("question from user:" + question)
                messages.append({"role": "user", "content": question})
                
                # send to open ai for answer
                progress(40,"sending to openAI...")
                answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages) 
                
                    # START find ID and episodes number of updated anime
                # The regex pattern             
                pattern = r"id:(\d+), episodes:(\d+)" if content_type == "anime" else r"id:(\d+), chapters:(\d+)" 
                # Use re.search to find the pattern in the text
                match = re.search(pattern, answer)

                if match:
                    # match.group(1) contains the id, match.group(2) contains the episodes number
                    updated_id = match.group(1)
                    updated_info = match.group(2)
                    print(f"id: {updated_id}, {content_type}: {updated_info}")
                else:
                    print("No match found")
                # END find ID and episodes number of updated anime/manga

                print_response_label(answer) # CHANGE THIS TO MORE HUMAN LIKE

                # send upgrade api do anilist 
                progress(50,"sending to anilist...")
                anilist_api_requests.change_progress(updated_id, updated_info,content_type)
                progress(55,"updated anilist database...")         
                # end anilist api
                
                    # FOR ARROWS TO PREVIOUS ANSWERS
                add_answer_to_history(answer)
                current_answer_index = len(answer_history) - 1
                    # END OF ARROWS TO PREVIOUS ANSWERS
                progress(60,"got answer")

                if tts_or_not == "Yes":
                    request_voice.request_voice_fn(f"Done, updated it to {updated_info} {content_type}")
                    progress(70,"got voice")
                    play_audio_fn("response")

                print("ShiroAi-chan: " + answer)

                # Save to database
                progress(80,"saving to DB...")
                connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
                connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                print("---------------------------------")
  
                beep = "cute_beep" #END OF ANSWER
                play_audio_fn(beep)

                    #show history in text widget
                progress(90,"showing in text box...")
                #show_history_from_db_widget.delete('1.0', 'end')
                display_messages_from_database_only(take_history_from_database())
   
                progress(100,"updated on anilist")

                running = False
                anilist_mode = False
                content_type_mode =""

            else: # continue if user does not want to exit
                
                # to database
                question = f"Madrus: {question}"
                print("question from user:" + question)
                messages.append({"role": "user", "content": question})
                
                    # send to open ai for answer
                progress(40,"sending to openAI...") 
                print("messages: " + str(messages))
                answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages) 
                print_response_label(answer)
                
                    # FOR ARROWS TO PREVIOUS ANSWERS
                add_answer_to_history(answer)
                current_answer_index = len(answer_history) - 1
                    # END OF ARROWS TO PREVIOUS ANSWERS

                progress(60,"got answer") 

                if tts_or_not == "Yes": #IF YES THEN WITH VOICE
                    request_voice.request_voice_fn(answer) #request Azure TTS to for answer
                    progress(70,"got voice")
                    play_audio_fn("response")
                    

                print("ShiroAi-chan: " + answer)
                
                
                if profanity.contains_profanity(answer) == True:
                    answer = profanity.censor(answer)                    
                progress(80,"saving to DB...")
                connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
                connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
                connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                print("---------------------------------")

                beep = "cute_beep" #END OF ANSWER
                play_audio_fn(beep)

                    #show history in text widget
                progress(90,"showing in text box...")
                #show_history_from_db_widget.delete('1.0', 'end')
                display_messages_from_database_only(take_history_from_database())
                

                running = False
                progress(100,"saved to DB, done")
                        
    
                    
        

           
    # Replace `print()` statements with `print_response()`
            # ...

def button_update_anilist_thread(media_type: str):
    """shows anime/manga in output box"""
    voice_thread = threading.Thread(target=button_show_anilist(media_type))
    voice_thread.start()  


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




# GUI elements
root = tk.Tk()
root.title("ShiroAi-chan Control Panel")

keyboard.on_press_key("F10", on_ctrl_press)  # Replace "ctrl+alt" with the desired key combination


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
    command=lambda: button_update_anilist_thread("ANIME"),
    relief="flat"
)
button_16.place(
    x=12.0,
    y=438.0,
    width=42.0,
    height=42.0
)
tooltip = ToolTip(button_16, "It shows my recent anime watched list")


button_image_17 = PhotoImage(
    file=relative_to_assets("button_17.png"))
button_17 = Button(
    image=button_image_17,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: button_update_anilist_thread("MANGA"),
    relief="flat"
)
button_17.place(
    x=66.0,
    y=487.0,
    width=42.0,
    height=42.0
)
tooltip = ToolTip(button_17, "It shows my recent manga read list")

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

    # for TSS voice tts_or_not
mute_or_unmute = tk.StringVar()
mute_or_unmute.set("Yes")
mute_or_unmute_yes = ttk.Radiobutton(root, text=" voice", variable=mute_or_unmute, value="Yes", style="Custom.TRadiobutton")
mute_or_unmute_no = ttk.Radiobutton(root, text=" no voice", variable=mute_or_unmute, value="No", style="Custom.TRadiobutton")
mute_or_unmute_yes.place(x=169, y=17)
mute_or_unmute_no.place(x=169, y=50)

    # for random speaking tts_or_not
talk_or_not = tk.StringVar()
talk_or_not.set("No")
talk_or_not.trace("w", on_talk_or_not_change) #this is looking for changes of state
talk_or_not_yes = ttk.Radiobutton(root, text=" talkative", variable=talk_or_not, value="Yes", style="Custom.TRadiobutton")
talk_or_not_no = ttk.Radiobutton(root, text=" sleeping...", variable=talk_or_not, value="No", style="Custom.TRadiobutton")
talk_or_not_yes.place(x=499, y=350)
talk_or_not_no.place(x=499, y=383)

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
running = False
thread_running = False
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()




