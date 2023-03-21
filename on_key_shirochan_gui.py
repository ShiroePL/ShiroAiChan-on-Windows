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


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")

# Initialize the question to speech engine 
engine=pyttsx3.init()
conn = None
api = None
global stop_listening_flag
stop_listening_flag = False
global recording_key
recording_key = False
default_user = "shiroe"
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
    #print("Playing voice")

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
        show_history_from_db_widget.insert(tk.END, f"{content}\n", 'center')
        show_history_from_db_widget.insert(tk.END, "\n")
    show_history_from_db_widget.see('end')



def voice_control():
    global stop_listening_flag
    global running
    stop_listening_flag = False
    global current_answer_index

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
        update_progress_bar(10), print_log_label("recording...")

        beep = "cute_beep" #started recording
        play_audio_fn(beep)

        print("Started recording: say you question NOW")

        question_file = "question"
        filename = f"./kiki_hub/{question_file}.wav"

        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            source.pause_threshold = 1 #this is the end of my speaking, but before saving it to file

        
            audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
            
            if stop_listening_flag:
                print("Stopped recording on user request via clicking button")
                print("---------------------------------")  # Check if the stop_listening button was pressed
                update_progress_bar(0), print_log_label("stopped rec. test raz dwa trzy cztery")
                beep = "cute_beep" #NEEEEEEEEEEEEEEESD TO FIND ANOTHER SOUND
                play_audio_fn(beep)
                break
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())
            f.close()

            update_progress_bar(20), print_log_label("transcribing...") #recorded audio

            try:  
                print("---------------------------------")
                
  
                question = transcribe_audio_question(question_file)
                cleaned_question = question.translate(str.maketrans("", "", string.punctuation)).strip().lower()
                
                if profanity.contains_profanity(question) == True: #dcensor question words for openAI send
                    question = profanity.censor(answer)

                if question:

                    update_progress_bar(30),print_log_label("transcribed.")

                    if cleaned_question in ("bye bye shiro", "exit program", "bye bye shira"):
                        beep = "cute_beep" #NEEEEEEEEEEEEEEESD TO FIND ANOTHER SOUND
                        play_audio_fn(beep)    
                        sys.exit()
                    else:               
                            #to database 
                        question = f"{name}: {question}"
                            #add question line to messages list
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

                        request_voice.request_voice_fn(answer) #request Azure TTS to for answer

                        update_progress_bar(70), print_log_label("got voice")

                        print("ShiroAi-chan: " + answer)
                        play_audio_fn("response")
                        
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
    name = user_name_entry.get()
    connect_to_phpmyadmin.check_user_in_database(name)
    history_from_database = connect_to_phpmyadmin.only_conversation_history_from_database(name)
    return history_from_database

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
    257.0,
    12.0,
    anchor="nw",
    text="ShiroAi-chan Control Panel",
    fill="#12D4FF",
    font=("Inter Bold", 48 * -1)
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
    x=52.0,
    y=91.0,
    width=127.0,
    height=51.0
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
    x=204.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: (connect_to_phpmyadmin.reset_chat_history(user_name_entry.get()), print_log_label("reset chat history")),
    relief="flat"
)
button_3.place(
    x=356.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: display_messages_from_database_only(take_history_from_database()),
    relief="flat"
)
button_4.place(
    x=508.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=connect_to_vtube,
    relief="flat"
)
button_5.place(
    x=52.0,
    y=165.0,
    width=127.0,
    height=51.0
)

tooltip = ToolTip(button_5, "This is the description of the button.")


button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=disconnect_from_vtube,
    relief="flat"
)
button_6.place(
    x=204.0,
    y=165.0,
    width=127.0,
    height=51.0
)

button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: api.play_animation("introduce"),
    relief="flat"
)
button_7.place(
    x=356.0,
    y=165.0,
    width=127.0,
    height=51.0
)

left_arrow_img = PhotoImage(
    file=relative_to_assets("left_arrow.png"))
left_arrow = Button(
    image=left_arrow_img,
    borderwidth=0,
    highlightthickness=0,
    command=show_previous_answer,
    relief="flat"
)
left_arrow.place(
    x=3.0,
    y=217.0,
    width=30.0,
    height=18.0
)

right_arrow_img = PhotoImage(
    file=relative_to_assets("right_arrow.png"))
right_arrow = Button(
    image=right_arrow_img,
    borderwidth=0,
    highlightthickness=0,
    command=show_next_answer,
    relief="flat"
)
right_arrow.place(
    x=40.0,
    y=217.0,
    width=30.0,
    height=18.0
)


button_image_10 = PhotoImage(
    file=relative_to_assets("button_10.png"))
button_10 = Button(
    image=button_image_10,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_10 clicked"),
    relief="flat"
)
button_10.place(
    x=3.0,
    y=240.0,
    width=42.0,
    height=42.0
)

tooltip = ToolTip(button_10, "Show persona description for current table.")

button_image_11 = PhotoImage(
    file=relative_to_assets("button_11.png"))
button_11 = Button(
    image=button_image_11,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: show_history_from_db_widget.delete('1.0', 'end'),
    relief="flat"
)
button_11.place(
    x=133.0,
    y=545.0,
    width=42.0,
    height=42.0
)

tooltip = ToolTip(button_11, "Clean text box below.")

button_image_12 = PhotoImage(
    file=relative_to_assets("button_12.png"))
button_12 = Button(
    image=button_image_12,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_12 clicked"),
    relief="flat"
)
button_12.place(
    x=211.0,
    y=545.0,
    width=42.0,
    height=42.0
)

tooltip = ToolTip(button_12, "Show all descriptions of persona.")

button_image_13 = PhotoImage(
    file=relative_to_assets("button_13.png"))
button_13 = Button(
    image=button_image_13,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_13 clicked"),
    relief="flat"
)
button_13.place(
    x=289.0,
    y=545.0,
    width=42.0,
    height=42.0
)

tooltip = ToolTip(button_13, "Insert new description to current table.")


entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    113.0,
    52.0,
    image=entry_image_1
)


user_name_entry = Entry(
    bd=0,
    bg="#7FD7EC",
    fg="#000716",
    highlightthickness=0
)
user_name_entry.place(
    x=52.0,
    y=35.0,
    width=122.0,
    height=32.0
)

user_name_entry.insert(0, default_user)

canvas.create_text(
    58.0,
    5.0,
    anchor="nw",
    text="Your name:",
    fill="#7FD5EA",
    font=("Inter Bold", 20 * -1)
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

style.configure("Custom.TRadiobutton", background="#000000", foreground="#FFFFFF", font=("Helvetica", 12))
style.map("Custom.TRadiobutton", background=[("active", "#000000")])

# Create custom images for the radio button states
normal_image = tk.PhotoImage(width=16, height=16)
selected_image = tk.PhotoImage(width=16, height=16)

# Fill in the images with the desired color and shape
normal_image.put(("black",), to=(0, 0, 16, 16))
selected_image.put(("red",), to=(0, 0, 16, 16))

# Draw arrow-like shape on the selected image
selected_image.put(("black",), to=(2, 7, 14, 9))
selected_image.put(("black",), to=(7, 2, 9, 14))

style.element_create("Custom.TRadiobutton.indicator", "image", normal_image,
                     ("selected", selected_image),
                     sticky="", padding=2)


reset_database_var = tk.StringVar()
reset_database_var.set("No")
reset_database_yes = ttk.Radiobutton(root, text="Yes", variable=reset_database_var, value="Yes", style="Custom.TRadiobutton")
reset_database_no = ttk.Radiobutton(root, text="No", variable=reset_database_var, value="No", style="Custom.TRadiobutton")
reset_database_yes.place(x=195, y=25)
reset_database_no.place(x=195, y=55)

#OMG RADIO BUTTONS ENDDD--------------------------------------------------------------------------------------------------





# PROGRESS BARRRRRRRRRRRRRRRRRRRR OMGGGGGGGGGGGGGGG
background_image = Image.open("./assets/frame0/progress_background.png")
filled_image = Image.open("./assets/frame0/progress_filled.png")

progress_width, progress_height = background_image.size

background_photo = ImageTk.PhotoImage(background_image)

canvas = tk.Canvas(root, width=progress_width, height=progress_height,bg="black", highlightthickness=0, bd=0, relief='ridge')
canvas.place(x=508, y=165)

background_progress = canvas.create_image(0, 0, anchor=tk.NW, image=background_photo)
filled_progress = canvas.create_image(0, 0, anchor=tk.NW)
# END PROGRESS BARRRRRRRRRRRRRRRRRRRR OMGGGGGGGGGGGGGGG



response_label = tk.Label(
    root,
    text="",
    bg="black",
    fg="#F9C6B3",
    font=("Inter Regular", 16),
    wraplength=410,
    anchor="center",  # Centers the text vertically
    justify="center",  # Centers the text horizontally
    width=26,  # Adjust this value to control the width of the label
)
response_label.place(
    x=52,
    y=240,
)

response_widget = tk.Text(root, wrap=tk.WORD, padx=10, pady=10, width=40, height=10,
                      bg='black', fg='#F9C6B3', font=("Inter Regular", 14),  bd=0)
response_widget.place(x=52, y=240, width=450, height=210)





            # i think i will change this to show_history_from_db_widget
log_label = tk.Label(
    root,
    text="",
    bg="black",
    fg="#12D4FF",
    font=("Inter Bold", 12 * -1),
    wraplength=110,
    anchor="center",  # Centers the text vertically
    justify="center",  # Centers the text horizontally
    width=15,  # Adjust this value to control the width of the label
)
log_label.place(
    x=515,
    y=185,
)

# Create the Text widget
show_history_from_db_widget = tk.Text(root, wrap=tk.WORD, padx=10, pady=10, width=40, height=10,
                      bg='black', fg='#12D4FF', font=("Inter Bold", 9),  bd=0)
show_history_from_db_widget.place(x=10, y=590, width=450, height=200)
show_history_from_db_widget.see('end')
# Create a Scrollbar and associate it with the Text widget
# scrollbar = ttk.Scrollbar(root, command=show_history_from_db_widget.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# show_history_from_db_widget.config(yscrollcommand=scrollbar.set)

# name = user_name_entry.get()
# connect_to_phpmyadmin.check_user_in_database(name)
# history_from_database = connect_to_phpmyadmin.only_conversation_history_from_database(name)

# for message in history_from_database:
#     print("Role: " + message["role"] + ", content: " + message["content"])
    
# print("History from database: " + str(history_from_database))



# Display the messages in the Text widget
display_messages_from_database_only(take_history_from_database())

show_history_from_db_widget.see('end')







root.resizable(False, False)
running = False
thread_running = False
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()




