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
from tkinter import *
from vtube_studio_api import VTubeStudioAPI


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")

# Initialize the question to speech engine 
engine=pyttsx3.init()
conn = None
api = VTubeStudioAPI()



windll.shcore.SetProcessDpiAwareness(1)
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
    chunk = 1024
    wf = wave.open(f'./kiki_hub/{filename}.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Playing voice")
# Replace print() statements with this function
# def print_response(response):
#     response_area.insert(tk.END, response + '\n')
#     response_area.see(tk.END)
def print_response_label(response):
    response_label.config(text=response)
    
    

def voice_control():
    # don't knwo why but without this it doesn't work probably because : with sr.Microphone() as source:
    name = user_name_entry.get()
    choice = reset_database_var.get()
    print("Your name?: " + name)
    print("Do you want to reset your chat history? You chose: " + choice)
    print("say 'exit program' to exit the program")
    
    if choice == "Yes":
        connect_to_phpmyadmin.reset_chat_history(name)
        
    connect_to_phpmyadmin.check_user_in_database(name)
    recognizer = sr.Recognizer() 


    print("started lintening")
    while running: #while runnign is true
        
        #print_response("Say 'pathfinder' to start a conversation")
        messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
        #Wait for user to say "pathfinder"
        print("Say 'pathfinder' to start a conversation")

        progress_var.set(0)

        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            alias = "alias"
            transcribed = f"./kiki_hub/{alias}.wav"
            with open(transcribed, "wb") as f:
                f.write(audio.get_wav_data())
            f.close()
            
            progress_var.set(50) 

            try:
                transcription = transcribe_audio_question(alias) #make transcription from alias file
                
                progress_var.set(100) 
                
                #print_response(transcription)
                print_response_label(transcription)
                if transcription.rstrip('.,?!').lower() == " exit program":
                    sys.exit()
                if transcription.rstrip('.,?!').replace(' ', '').lower() == "pathfinder":
                        #record audio
                    question_file = "question"
                    filename = f"./kiki_hub/{question_file}.wav"
                    print("---------------------------------")
                    print("Say your question")
                    beep = "cute_beep"
                    play_audio_fn(beep)
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                        f.close()           
                    #transcript audio to question 
                    question = transcribe_audio_question(question_file)
                    
                    if question:
                            #to database
                        question = f"{name}: {question}"
                            #add question line to messages list
                        messages.append({"role": "user", "content": question})
                            # send to open ai for answer
                        answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages)        
                        request_voice.request_voice_fn(answer) #request Azure TTS to for answer
                        
                        print("ShiroAi-chan: " + answer)
                        play_audio_fn("response")
                        
                        if profanity.contains_profanity(answer) == True:
                            answer = profanity.censor(answer)                    

                        connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
                        connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
                        connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                        print("---------------------------------")

                        if transcribed == " exit program":
                            print("exiting program")
                            sys.exit()
            except Exception as e:
                print("An error occurred: {}".format(e))
    # Replace `print()` statements with `print_response()`
            # ...



def start_voice_control():
    global running
    running = True #will start the while loop in voice control
    voice_thread = threading.Thread(target=voice_control)
    voice_thread.start()


def stop_listening():
    global running
    running = False #will cut off the while loop in voice control
    

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def on_closing():
    api.close()
    root.destroy()



# GUI elements
root = tk.Tk()
root.title("ShiroAi-chan Control Panel")


root.geometry("1000x600")
root.configure(bg = "#4B98E0")

canvas = Canvas(
    root,
    bg = "#4B98E0",
    height = 600,
    width = 1000,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    500.0,
    300.0,
    image=image_image_1
)

canvas.create_text(
    204.0,
    7.0,
    anchor="nw",
    text="ShiroAi-chan Control Panel",
    fill="#F9C6B3",
    font=("Inter Bold", 40 * -1)
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
start_button = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=start_voice_control,
    relief="flat"
)


start_button.place(
    x=64.0,
    y=69.0,
    width=120.0,
    height=50.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
stop_button = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=stop_listening,
    relief="flat"
)


stop_button.place(
    x=225.0,
    y=66.0,
    width=120.0,
    height=53.0
)

play_animation_button = tk.Button(root, text="Play Animation", command=lambda: api.play_animation("introduce"))
play_animation_button.place(
    x=225.0,
    y=466.0,
    width=120.0,
    height=53.0
)



# frame = tk.Frame(root)
# frame.pack(padx=10, pady=10)

#start_button = tk.Button(root, command=start_voice_control)
#start_button.grid(row=0, column=0, padx=5, pady=5)


#stop_button = tk.Button(root, command=stop_listening)
#stop_button.grid(row=0, column=1, padx=5, pady=5)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    124.5,
    168.0,
    image=entry_image_1
)


user_name_entry = Entry(
    bd=0,
    bg="#FFDDD3",
    fg="#000716",
    highlightthickness=0
)
user_name_entry.place(
    x=53.0,
    y=151.0,
    width=143.0,
    height=32.0
)

# Create the Radiobutton widgets
style = ttk.Style()
style.theme_use("default")
style.configure("TRadiobutton", font=("Helvetica", 12), background="#E6E6E6", foreground="#333333")
reset_database_var = StringVar()
reset_database_var.set("No")
reset_database_yes = ttk.Radiobutton(root, text="Yes", variable=reset_database_var, value="Yes")
reset_database_no = ttk.Radiobutton(root, text="No", variable=reset_database_var, value="No")
reset_database_yes.place(x=100, y=200)
reset_database_no.place(x=170, y=200)

# Create the ProgressBar widget
progress_var = IntVar()
progress_bar = ttk.Progressbar(root, maximum=100, variable=progress_var)
progress_bar.place(x=240, y=200)










response_label = tk.Label(
    root,
    text="",
    bg=root.cget("bg"),
    fg="#F9C6B3",
    font=("Inter Regular", 16),
    wraplength=300,
    anchor="center",  # Centers the text vertically
    justify="center",  # Centers the text horizontally
    width=30,  # Adjust this value to control the width of the label
)
response_label.place(
    x=100,
    y=230,
)

canvas.create_text(
    31.0,
    119.0,
    anchor="nw",
    text="name:",
    fill="#FFFFFF",
    font=("Inter Regular", 24 * -1)
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    810.0,
    312.0,
    image=image_image_2
)

# response_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=10)
# response_area.grid(row=1, column=0, columnspan=3, padx=5, pady=5)


root.resizable(False, False)
running = False
thread_running = False
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
#root.protocol("WM_DELETE_WINDOW", on_closing)
# other_button = tk.Button(frame, text="Other Function", command=other_function)
# other_button.grid(row=0, column=2, padx=5, pady=5)





# response_label = tk.Label(root, text="", wraplength=300)
# response_label.pack()




