import threading
import tkinter as tk
from tkinter import ttk, BooleanVar
import speech_recognition as sr
import time 
import kiki_hub.request_whisper as request_whisper
import base64
import requests
import shared_code.connect_to_phpmyadmin as connect_to_phpmyadmin
from better_profanity import profanity
import shared_code.chatgpt_api
import kiki_hub.request_voice_tts as request_voice
import sys
from tkinter import Entry, Button, PhotoImage
from pathlib import Path
from ctypes import windll
from vtube_studio_api import VTubeStudioAPI
from PIL import Image, ImageTk
import string
import keyboard
import pygame
import shared_code.anilist.anilist_api_requests as anilist_api_requests
import re
import random
from shared_code.shiro_agent import CustomToolsAgent
from shared_code.langchain_database.langchain_vector_db_queries import search_db_with_llm_response, save_to_db
from shared_code.calendar_functions.test_wszystkiego import add_event_from_shiro, retrieve_plans_for_days
from shared_code.home_assistant import ha_api_requests, open_weather_api
from datetime import datetime

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")
windll.shcore.SetProcessDpiAwareness(1) #make window sharp on high dpi screens


conn = None
api = None
global stop_listening_flag
stop_listening_flag = False
global recording_key
state = ""
anilist_mode = False
content_type_mode =""
recording_key = False
hold_random_timer = 0
default_user = "normal"
font_family = "Baloo Bhai 2 SemiBold"
answer_history = [] #for local history of answers

class ToolTip:
    """This class is for displaying text when hovering on icons in Tkinter GUI."""
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


def agent_shiro(query):
    agent = CustomToolsAgent()
    final_answer = agent.run(query)
    print("final answer from agent: " + final_answer)
    return final_answer

def transcribe_audio_question(filename):
    """Transcribe the given audio from microphone on Windows using local Whisper model."""
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

def print_response_label(response):
    """Print the response to the response text widget in Tkinter GUI."""
    response_widget.configure(font=(font_family, 19 * -1))
    response_widget.delete('1.0', 'end')
    response_widget.insert(tk.END, f"{response}", 'center')
    response_widget.tag_configure('center', justify='center')
    response_widget.insert(tk.END, "\n")
   
def print_log_label(response):
    log_label.config(text=response)

def reformat_list_output(data_str, type:str):
    """Format the data as a table with 3 columns.

    type is anime or manga"""
    entries = data_str.split('\n')
    table_data = []
    pattern = r'^romaji_title:(.*), id:(\d+), read_chapters:(.*)$' if type == "manga" else r'^romaji_title:(.*), id:(\d+), watched_episodes:(.*)$'
    
    for entry in entries:
        if entry.strip():  # Exclude empty strings
            match = re.search(pattern, entry.strip())
            if match:
                title = match.group(1)
                id_str = match.group(2)
                read_chapters = match.group(3)
                
                if type == "manga":
                    table_data.append({"Title": title, "ID": id_str, "Read Chapters": read_chapters})
                else:
                    table_data.append({"Title": title, "ID": id_str, "Watched Episodes": read_chapters})

    return table_data

def print_anime_list(table_data):
    """Print the response to the response text widget in Tkinter GUI."""
    
    # Build a formatted string from the table data
    formatted_str = ""
    for row in table_data:
        formatted_str += f"Title: {row['Title']}\n"
        formatted_str += f"ID: {row['ID']}\n"
        if 'Read Chapters' in row:
            formatted_str += f"Read Chapters: {row['Read Chapters']}\n"
        else:
            formatted_str += f"Watched Episodes: {row['Watched Episodes']}\n"
        formatted_str += "-" * 40 + "\n"  # Separator
    
    # Display the formatted string in the Tkinter text widget
    
    response_widget.configure(font=(font_family, 10))  # Update font to Helvetica, size 10
    response_widget.delete('1.0', 'end')
    response_widget.insert(tk.END, f"{formatted_str}", 'center')
    response_widget.tag_configure('center', justify='center')
    response_widget.insert(tk.END, "\n")

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

def stop_audio():   
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    print("Stopped Shiro :O")
            
# ----------- START FUNCTIONS FOR THE arrows-----------
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

# ----------- END FUNCTIONS FOR THE arrows---------

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
        show_history_from_db_widget.insert(tk.END, f"\nRole: {role}\n", 'center')
        show_history_from_db_widget.tag_configure('center', justify='center')
        show_history_from_db_widget.insert(tk.END, f"{content}", 'center')
        
    show_history_from_db_widget.see('end')

def show_room_temperature():
    name = table_name_input.get()
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
    question = "can you show me my room temperature?"
    query = f"[current time: {current_time}] {question}"
    
        # use function chain to add event to calendar
    answer_from_ha = ha_api_requests.room_temp()
    outside_temperature = open_weather_api.current_temperature()
    print("answer from api: " + answer_from_ha)
    progress(60,"got temperature, adding personality...")
    query2 = f"[current time: {current_time}] Madrus: {query}. shiro: Retriving informations from her sensors... Done! Info from sensors:{answer_from_ha}°C. Weather outside: {outside_temperature}°C.| (please say °C in your answer) | Shiro:"
    messages.append({"role": "user", "content": query2})
    
    print("messages: " + str(messages))

        # add personality to answer
    personalized_answer, prompt_tokens, completion_tokens, total_tokens = shared_code.chatgpt_api.send_to_openai(messages)

    print_response_label(personalized_answer)
    
    repetitive_part_of_voice_control_functions_tokens(name, query, personalized_answer, messages, prompt_tokens, completion_tokens, total_tokens)

    progress(100,"showed, done")          

################################### RANDOM QUESTIONS FROM SHIRO ######################################################


timer_running = False
timer_thread = None
stop_event = threading.Event()

def on_talk_or_not_change(*args):
    """Callback for when the user changes talkative checkbox"""
    if talk_or_not.get() == "Yes":
        start_timer()
    else:
        stop_timer()

   
def start_timer():
    """starts timer for random questions in separate thread"""
    global timer_running
    global timer_thread
    timer_running = True
    stop_event.clear()
    timer_thread = threading.Thread(target=timer_for_random_questions)
    timer_thread.start()

def stop_timer():
    global timer_running
    global timer_thread
    timer_running = False
    stop_event.set()
    if timer_thread is not None:
        timer_thread.join()

def timer_for_random_questions():
    """this is the timer that counts down and runs ask question function"""
    while timer_running:
        ask_random_question()
        interval = random.randint(200, 300)  # Random interval between _ and _ seconds
        stop_event.wait(interval)

def ask_random_question(): # THIS SHIT IS FOR ASKING PROMPT
    print("-----START asking random question-----")

    question = f"Madrus: This is programmed functionality for you that is asking me questions from time to time. So ask me some question, can be random or based on what we talked before. But please make it short, not too long. And remember: if i will not say anything in answer to you(or this message will be repeated), ask me why i am not answering or am i still here."
    name = table_name_input.get()
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
    messages.append({"role": "user", "content": question})
        
    progress(40,"sending to openAI...") 
        # send to open ai for answer
    answer, prompt_tokens, completion_tokens, total_tokens = shared_code.chatgpt_api.send_to_openai(messages) 
    print_response_label(answer)

    repetitive_part_of_voice_control_functions_tokens(name, question, answer, messages, prompt_tokens, completion_tokens, total_tokens)  
    progress(100,"asking random question...")

    print("-----END asking random question-----")

##################################################################################################################################

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!REPETITIVE PART OF VOICE CONTROL FUNCTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def repetitive_part_of_voice_control_functions_tokens(name, question, answer,messages, prompt_tokens, completion_tokens, total_tokens, answer_for_tts = None):
    global tts_or_not
    global agent_mode
    tts_or_not = mute_or_unmute.get()

        # FOR ARROWS TO PREVIOUS ANSWERS
    add_answer_to_history(answer)
    current_answer_index = len(answer_history) - 1
        # END OF ARROWS TO PREVIOUS ANSWERS

    if tts_or_not == "Yes":
        # If answer_for_tts is provided, use it. If not, use 'answer' as before.
        request_voice.request_voice_fn(answer if answer_for_tts is None else answer_for_tts)
        progress(70,"got voice")
        
    
    progress(90,"showing in text box...")

    connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
    connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
    connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to A DB with usage stats
    
    display_messages_from_database_only(take_history_from_database())
    if tts_or_not == "Yes":
        play_audio_thread("response")
        beep = "cute_beep" #END OF ANSWER
        play_audio_fn(beep)

    progress(95,"addded tokens to db")
    
def repetitive_part_of_voice_control_functions(name, question, answer,messages, answer_for_tts = None):
    global tts_or_not
    global agent_mode
    tts_or_not = mute_or_unmute.get()

        # FOR ARROWS TO PREVIOUS ANSWERS
    add_answer_to_history(answer)
    current_answer_index = len(answer_history) - 1
        # END OF ARROWS TO PREVIOUS ANSWERS
    print("answer_for_tts: ",answer_for_tts)
    if tts_or_not == "Yes":
        
        request_voice.request_voice_fn(answer if answer_for_tts is None else answer_for_tts)
        progress(70,"got voice")

  
        #show history in text widget
    
    progress(90,"showing in text box...")
    
    connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
    connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
    
    display_messages_from_database_only(take_history_from_database())
    if tts_or_not == "Yes":
        play_audio_thread("response")
        beep = "cute_beep" #END OF ANSWER
        play_audio_fn(beep)
    progress(95,"addded tokens to db")
    
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!END OF REPETITIVE PART OF FUNCTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def voice_control(input_text=None):
    global stop_listening_flag
    global running
    global hold_random_timer
    stop_listening_flag = False
    global current_answer_index

    name = table_name_input.get()  # takes name from input
    tts_or_not = mute_or_unmute.get() # takes tts mode from checkbox
    
        # hold random questions if i am conversing so she will not ask me in the middle of conversation
    if talk_or_not.get() == "Yes":
        talk_or_not.set("No")
        print("----checkbox putted on SLEEPING----")
    
    print("Your name?: " + name)
    print("Do you want voice? You chose: " + tts_or_not)
    print("say 'exit program' to exit the program")

    connect_to_phpmyadmin.check_user_in_database(name)
    recognizer = sr.Recognizer()
    
    while running:  # while running is true
        global anilist_mode
        global content_type_mode
        messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
        agent_reply = ''

        if input_text is None: #if input text is none then listen to microphone input
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

        # Get all punctuation but leave colon ':'
        punctuation_without_colon = "".join([ch for ch in string.punctuation if ch != ":"])

        cleaned_question = question.translate(str.maketrans("", "", punctuation_without_colon)).strip().lower()

                # CHECK IF IT IS AGENT MODE 
        if cleaned_question.startswith("agent:") or agent_mode.get()  or cleaned_question.startswith("agent mode"):
            print("wejscie w if od agenta ")
            progress(10,"entering agent mode...")
            cleaned_question = cleaned_question.replace("agent:", "").strip()
            agent_reply = agent_shiro(cleaned_question)
            progress(20,"agent mode: " + agent_reply)
            print("Agent: " + agent_reply)

        if profanity.contains_profanity(question):
            question = profanity.censor(answer) # censor question words for openAI send

        if question:
                # check if question was asked using voice or input
            progress(30,"transcribed.") if input_text is None else progress(30,"question given in input.")
                # end if user wants to exit
            if cleaned_question in ("bye bye shiro", "exit program", "bye bye shira"):
                beep = "cute_beep"  # NEEEEEEEEEEEEEEED TO FIND ANOTHER SOUND
                play_audio_fn(beep)
                sys.exit()


            elif cleaned_question.lower().startswith("plan:") or "add_event_to_calendar" in agent_reply:
                print("---------add event to calendar---------")
                """add event to calendar"""
                query = cleaned_question.replace("plan:", "").strip()
                messages.append({"role": "user", "content": query})
                progress(30,"adding event to calendar...")
                # use chain to add event to calendar
                answer, prompt_tokens, completion_tokens, total_tokens, formatted_query_to_calendar = add_event_from_shiro(query)

                progress(60,"event added")
                print_response_label("I added event with this info: \n" + formatted_query_to_calendar)
                answer_for_tts = "I added event with provided informations."

                repetitive_part_of_voice_control_functions_tokens(name, query, answer, messages, prompt_tokens, completion_tokens, total_tokens, answer_for_tts)
        
                running = False
                progress(100,"showed, done")    
             
            elif cleaned_question.lower().startswith("schedule:") or "retrieve_event_from_calendar" in agent_reply:
                """retrieve event from calendar"""
                print("---------retrieve event from calendar---------")
                query = cleaned_question.replace("schedule:", "").strip()
                query = "Madrus: " + query
                messages.append({"role": "user", "content": query})
                progress(30,"retrieving event from calendar...")
                # use function chain to add event to calendar
                answer, prompt_tokens, completion_tokens, total_tokens = retrieve_plans_for_days(query)

                progress(60,"got schedule, adding personality...")

                    # sending schedule to shiro to add personality to raw schedule
                question = f"""can you summarize my plans ? what i have for that days. tell me like assistant tells plans for her boss when he has little time to listen. In 'your words', not just plain date's. and please order it by dates. here are my plans: '{answer}"""
                
                messages.append({"role": "user", "content": question})
                        
                print("messages: " + str(messages))
                personalized_answer, prompt_tokens2, completion_tokens2, total_tokens2 = shared_code.chatgpt_api.send_to_openai(messages)

                prompt_tokens += prompt_tokens2
                completion_tokens += completion_tokens2
                total_tokens += total_tokens2

                print_response_label(personalized_answer)
                print("answer: " + answer)
                repetitive_part_of_voice_control_functions_tokens(name, query, personalized_answer, messages, prompt_tokens, completion_tokens, total_tokens)
        
                running = False
                progress(100,"showed, done")
               
            elif cleaned_question.lower().startswith("ha:") or "home_assistant" in agent_reply: # show room temperature
                print("---------show room temperature---------")
                """show room temperature"""
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
                query = cleaned_question.replace("ha:", "").strip()
                query = f"[current time: {current_time}] {query}"
                progress(30,"getting temperature...")
                    # use function chain to add event to calendar
                answer_from_ha = ha_api_requests.room_temp()
                outside_temperature = open_weather_api.current_temperature()
                print("answer from api: " + answer_from_ha)
                progress(60,"got temperature, adding personality...")
                query2 = f"[current time: {current_time}] Madrus: {query}. shiro: Retriving informations from her sensors... Done! Info from sensors:{answer_from_ha}°C. Weather outside: {outside_temperature}°C.| (please say °C in your answer) | Shiro:"
                messages.append({"role": "user", "content": query2})
                
                print("messages: " + str(messages))

                    # add personality to answer
                personalized_answer, prompt_tokens, completion_tokens, total_tokens = shared_code.chatgpt_api.send_to_openai(messages)

                print_response_label(personalized_answer)
                
                repetitive_part_of_voice_control_functions_tokens(name, query, personalized_answer, messages, prompt_tokens, completion_tokens, total_tokens)
        
                running = False
                progress(100,"showed, done")          
             
            elif cleaned_question.lower().startswith("db:") or "database_search" in agent_reply or search_chromadb.get():
                print("---------vector db mode ENTERED---------")
                query = cleaned_question.replace("db:", "").strip()
                messages.append({"role": "user", "content": query})
                progress(30,"Searching db...")
                answer = search_db_with_llm_response(query)
                print("answer from db: " + str(answer))
                progress(60,"Found something!")
                print_response_label(answer)
                
                repetitive_part_of_voice_control_functions(name, cleaned_question, answer, messages)
                
                running = False
                progress(100,"showed, done")
            
            elif "show_anime_list" in agent_reply or "show_manga_list" in agent_reply or "showmangalist" in cleaned_question or "showanimelist" in cleaned_question:
                """show anime/manga list"""
                print("---------show anime/manga list---------")
                
                if agent_reply == "":
                    content_type = "anime" if "showanimelist" in cleaned_question else "manga"
                else:
                    content_type = "anime" if "anime" in agent_reply else "manga"
                progress(30,"getting list...")
                list_content, _ = anilist_api_requests.get_10_newest_entries("ANIME") if content_type == "anime" else anilist_api_requests.get_10_newest_entries("MANGA")  

                print_response_label(f"Here is your list of most recent {content_type}.{list_content}")

                reformated_list = reformat_list_output(list_content, content_type)
                print_anime_list(reformated_list)
                progress(60,"got list")
                print("lista: \n" + list_content) # for testing
                answer = "Here is your list of most recent " + content_type + "." + list_content
                repetitive_part_of_voice_control_functions(name, question, answer, messages, f"Here is your list of most recent {content_type}")
                   
                running = False 
                
                progress(100,"showed, done")
            elif update_list_checkbox.get(): # she is in animelist mode, so she remembers list i gave her
                    # make shiro find me id of anime/manga
                    
                if "manga" in question.lower() or "anime" in question.lower():
                    """update anime/manga list"""
                    print("---------update anime/manga list---------")
                    if "manga" in question.lower():
                        content_type = "manga"
                    else:
                        content_type = "anime"

                    content_type = "manga" if "manga" in question.lower() else "anime"
                    progress(30,"getting list...")
                        ##### we need to ger anime/manga list
                    list_content, _ = anilist_api_requests.get_10_newest_entries("ANIME") if content_type == "anime" else anilist_api_requests.get_10_newest_entries("MANGA")
                    fake_question = f"Madrus: I will give you list of my 10 most recent watched/read {content_type} from site AniList. Here is this list:{list_content}. I want you to remember this because in next question I will ask you to update episodes/chapters of one of them."
                    messages.append({"role": "user", "content": fake_question})

                        # add as answer
                    answer = "Okay, I will remember it, Madrus. I'm waiting for your next question. Give it to me nyaa."
                    messages.append({"role": "assistant", "content": answer})
                    

                    end_question = "I would like you to answer me giving me ONLY THIS: ' title:<title>,id:<id>,"
                    extra = " episodes:<episodes>'. Nothing more." if content_type == "anime" else " chapters:<chapters>'. Nothing more."
                    question = f"Madrus: {question}. {end_question}{extra}"

                    messages.append({"role": "user", "content": question})
                    
                    # send to open ai for answer
                    progress(40,"sending to openAI...")
                    answer, prompt_tokens, completion_tokens, total_tokens = shared_code.chatgpt_api.send_to_openai(messages) 
                              
                    pattern = r"id:\s*(\d+),\s*episodes:\s*(\d+)" if content_type == "anime" else r"id:\s*(\d+),\s*chapters:\s*(\d+)"

                    match = re.search(pattern, answer)

                    if match:
                        # match.group(1) contains the id, match.group(2) contains the episodes number
                        updated_id = match.group(1)
                        updated_info = match.group(2)
                        print(f"id: {updated_id}, {content_type}: {updated_info}")
                        print_response_label(answer) # CHANGE THIS TO MORE HUMAN LIKE

                        # send upgrade api do anilist 
                        progress(50,"sending to anilist...")
                        anilist_api_requests.change_progress(updated_id, updated_info,content_type)
                        progress(55,"updated anilist database...")         
                        # end anilist api
                        tts_answer = f"Okay, I updated {content_type} to {updated_info} episodes" if content_type == "anime" else f"Okay, I updated {content_type} to {updated_info} chapters"
                        repetitive_part_of_voice_control_functions_tokens(name, question, answer, messages, prompt_tokens, completion_tokens, total_tokens, tts_answer)
        
                        progress(100,"updated on anilist")
                    else:
                        print("No match found")
                        print_response_label("I'm sorry, I couldn't find the ID and episodes number of updated anime/manga. Please try again.")
                        #----- END find ID and episodes number of updated anime/manga-----


                running = False
                progress(100,"exited animelist mode")
                print("---------END---------")
            else: # continue if user does not want to exit
                """normal mode"""
                print("---------normal mode---------")
                print("cleanded question to to: " + cleaned_question)
                # to database
                question = f"Madrus: {question}"
                print("question from user:" + question)
                messages.append({"role": "user", "content": question})
                
                    # send to open ai for answer
                progress(40,"sending to openAI...") 
                print("messages: " + str(messages))
                answer, prompt_tokens, completion_tokens, total_tokens = shared_code.chatgpt_api.send_to_openai(messages) 
                print_response_label(answer)
                
                repetitive_part_of_voice_control_functions_tokens(name, question, answer, messages, prompt_tokens, completion_tokens, total_tokens)
                
                running = False
                progress(100,"saved to DB, done")
        # Create a new thread and start the timer
        if talk_or_not == "Yes":
            hold_timer_thread = threading.Thread(target=hold_timer)
            hold_timer_thread.start()
            print("timer for testing holding random questions STARTED")
            print_active_threads()
        else:
            print("timer for testing holding random questions NOT STARTED (talk_or_not = No)") 
            print_active_threads()                   
        print("------END------")
                    
def print_active_threads():
    threads = threading.enumerate()
    for thread in threads:
        print(thread)

def play_audio_thread(response: str):
    audio_thread = threading.Thread(target=play_audio_fn(response))
    audio_thread.start()

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

def show_temperature_button():
    global running
    running = True #will start the while loop in voice control
    voice_thread = threading.Thread(target=show_room_temperature)
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
    canvas2.itemconfig(filled_progress, image=filled_photo)
    canvas2.image = filled_photo  # Keep a reference to the image object to prevent garbage collection

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
    descriptions = connect_to_phpmyadmin.get_all_descriptions()
    response_widget.delete('1.0', 'end')
        # Display the descriptions in the Text widget
    for description in descriptions:
        response_widget.insert(tk.END, f"{description['id']}: {description['description']}\n")
        response_widget.insert(tk.END, "\n")

def hold_timer():
    # Start the timer
    start_time = time.time()

    while True:
            # Calculate elapsed time
        elapsed_time = time.time() - start_time
            # If elapsed time is 20 seconds or more, break the loop
        if elapsed_time >= 20:
            break

    print("Timer stopped after 20 seconds.")
    root.after(0, talk_or_not.set, "Yes")

def reset_table_and_make_new():
    connect_to_phpmyadmin.reset_chat_history(table_name_input.get())
    print_log_label("reset chat history")
    display_messages_from_database_only(take_history_from_database())

def save_pdf(pdf: str, name_of_pdf: str):
    """Save the PDF to a file"""
    progress(20,"saving pdf...")
    print_log_label("saving pdf...")
    save_to_db(pdf,None,name_of_pdf)
    print_log_label("saved pdf to db")
    progress(100,"saved pdf to db")
    print_response_label(f"I added {name_of_pdf}.pdf to my database :) \n")

# GUI elements
root = tk.Tk()
root.title("ShiroAi-chan Control Panel")
keyboard.on_press_key("F10", on_ctrl_press)  # Replace "ctrl+alt" with the desired key combination
root.geometry("1200x800")
root.configure(bg = "#4B98E0")

canvas = tk.Canvas(
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
    command=reset_table_and_make_new,
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
    command=lambda: response_widget.delete('1.0', 'end'),
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
    x=139.0,
    y=534.0,
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
    x=201.0,
    y=534.0,
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
    x=263.0,
    y=534.0,
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
    x=325.0,
    y=534.0,
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
    command=lambda: start_voice_control_input("show_anime_list"),
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
    command=lambda: start_voice_control_input("show_manga_list"),
    relief="flat"
)
button_17.place(
    x=66.0,
    y=487.0,
    width=42.0,
    height=42.0
)
tooltip = ToolTip(button_17, "It shows my recent manga read list")

button_image_18 = PhotoImage(
    file=relative_to_assets("button_18.png"))
button_18 = Button(
    image=button_image_18,
    borderwidth=0,
    highlightthickness=0,
    command=show_temperature_button,
    relief="flat"
)
button_18.place(
    x=12.0,
    y=487.0,
    width=42.0,
    height=42.0
)
tooltip = ToolTip(button_18, "Show room temerature (using home assistant sensors")

button_image_speaking = PhotoImage(
    file=relative_to_assets("button_19.png"))
button_stop_speaking = Button(
    image=button_image_speaking,
    borderwidth=0,
    highlightthickness=0,
    command=stop_audio,
    relief="flat"
)
button_stop_speaking.place(
    x=525.0,
    y=440.0,
    width=42.0,
    height=42.0
)
tooltip = ToolTip(button_stop_speaking, "Stops shiro from speaking")

button_image_20 = PhotoImage(
    file=relative_to_assets("button_20.png"))
button_20 = Button(
    image=button_image_20,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: save_pdf("pdf", name_of_pdf=show_history_from_db_widget.get("1.0", tk.END).strip()),
    relief="flat"
)
button_20.place(
    x=387.0,
    y=534.0,
    width=42.0,
    height=42.0
)
tooltip = ToolTip(button_20, "Add PDF to vector database, to later ask about it's content, input JUST NAME of PDF file, without '.pdf'")

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

# Create image on canvas
image_image_dont_mute_me = PhotoImage(file="assets/frame0/dont_mute_me.png")  # Replace this with your actual image path
image_dont_mute_me = canvas.create_image(965.0, 100.0, image=image_image_dont_mute_me, tags="my_image11")
# Initialize global state variable
#
def hide_mute_or_not(*args):
    global mute_or_unmute
    """Callback for when the user changes talkative checkbox"""
    if mute_or_unmute.get() == "No":
        print("Setting image to normal (visible)")
        canvas.itemconfig("my_image11", state='normal')
        state = "Showing"
    elif mute_or_unmute.get() == "Yes":
        print("Setting image to hidden")
        canvas.itemconfig("my_image11", state='hidden')
        state = "Hidden"
    canvas.update()

# Create Radiobuttons with placement and custom style
mute_or_unmute = tk.StringVar()
mute_or_unmute.set("No")
mute_or_unmute.trace("w", hide_mute_or_not) #this is looking for changes of state
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

# search vector database aka PDF searching
search_chromadb = BooleanVar()
search_chromadb.set(False)  # Default value
# Create the checkbox
checkbox = ttk.Checkbutton(root, text="PDF searching", variable=search_chromadb, style="Custom.TRadiobutton")
checkbox.place(x=499, y=615)
   

# update anime/manga list
update_list_checkbox = BooleanVar()
update_list_checkbox.set(False)  # Default value
# Create the checkbox
checkbox = ttk.Checkbutton(root, text="Update list?", variable=update_list_checkbox, style="Custom.TRadiobutton")
checkbox.place(x=499, y=650)
   
# Create a variable to hold the checkbox state
agent_mode = BooleanVar()
agent_mode.set(False)  # Default value
agent_mode.trace("w", on_talk_or_not_change)  # This will look for changes of state
# Create the checkbox
checkbox = ttk.Checkbutton(root, text="Agent Mode", variable=agent_mode, style="Custom.TRadiobutton")
checkbox.place(x=499, y=685)


# PROGRESS BAR
background_image = Image.open("./assets/frame0/image_3.png")
filled_image = Image.open("./assets/frame0/image_4.png")

progress_width, progress_height = background_image.size
background_photo = ImageTk.PhotoImage(background_image)

canvas2 = tk.Canvas(root, width=progress_width, height=progress_height,bg="black", highlightthickness=0, bd=0, relief='ridge')
canvas2.place(x=543, y=136)

background_progress = canvas2.create_image(0, 0, anchor=tk.NW, image=background_photo)
filled_progress = canvas2.create_image(0, 0, anchor=tk.NW)
# END PROGRESS BAR

response_widget = tk.Text(root, wrap=tk.WORD, padx=10, pady=10, width=40, height=10,
                      bg='black', fg='#A8E1F6', font=(font_family, 19 * -1),  bd=0)
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

if hold_random_timer == 20000:
    hold_random_timer = 0
    print("timer for testing holding random questions RESETED") 
    talk_or_not.set("Yes")
    print("checkbox putted on TALKATIVE")
    stop_timer()
    
update_progress_bar(100)
root.resizable(False, False)
running = False
thread_running = False
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()