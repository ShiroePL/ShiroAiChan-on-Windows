from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
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
from shiro_agent import CustomToolsAgent
from langchain_database.answer_with_chromadb_huggingface_embedd import search_chroma_db
from langchain_database.test_wszystkiego import add_event_from_shiro

import connect_to_phpmyadmin
import shiro_on_android
app = FastAPI()



class QuestionWithUser(BaseModel):
    question: str
    username: str
    checkbox: bool

class ChatMessage(BaseModel):
    role: str
    content: str

def agent_shiro(query):
    agent = CustomToolsAgent()
    final_answer = agent.run(query)
    return final_answer

def exit_anilist_mode():
    global anilist_mode
    anilist_mode = False
    print("--------------------")
    print("exited anilist mode")
    print("--------------------")



@app.get("/chat_history/{name}")
async def get_chat_history(name: str):
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database("normal")
    return {"messages": messages}


@app.get("/audio/{audio_file_name}")
async def get_audio(audio_file_name: str):
    return FileResponse(f"./kiki_hub/{audio_file_name}")

@app.post("/question")
async def question(payload: QuestionWithUser):
    """
    A FastAPI endpoint to answer a question
    """
    question_text = payload.question
    username = payload.username
    checkbox = payload.checkbox  # This is the checkbox status
    
    #answer = shiro_on_android.voice_control(question_text, username, checkbox) #need to change this
    answer = main_function(question_text, checkbox, "normal")


    # Process the question, username and checkbox as needed
    done_answer = f" {answer}"
    return {"answer": done_answer}


def main_function(question, checkbox, name="normal"):

    agent_mode_variable = checkbox
    agent_reply = ''
    connect_to_phpmyadmin.check_user_in_database(name)
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
    global anilist_mode
    global content_type_mode

    
    # Get all punctuation but leave colon ':'
    punctuation_without_colon = "".join([ch for ch in string.punctuation if ch != ":"])
    cleaned_question = question.translate(str.maketrans("", "", punctuation_without_colon)).strip().lower()


    if agent_mode_variable == True or cleaned_question.startswith("agent mode"):
        print("wejscie w if od agenta ")
        
        cleaned_question = cleaned_question.replace("agent:", "").strip()
        agent_reply = agent_shiro(cleaned_question)
        
        print("Agent: " + agent_reply)


    if cleaned_question in ("stop:"):
        exit_anilist_mode()
        print("exited anilist mode")
        answer = "exited anilist mode"
        return answer
        

    elif cleaned_question.lower().startswith("plan:") or "add_event_to_calendar" in agent_reply:
        query = cleaned_question.replace("plan:", "").strip()

        messages.append({"role": "user", "content": query})
            # use chain to add event to calendar
        answer, prompt_tokens, completion_tokens, total_tokens, formatted_query_to_calendar = add_event_from_shiro(query)


        
        print("I added event with this info: \n" + formatted_query_to_calendar)
        answer = "I added event with this info: \n" + formatted_query_to_calendar

        request_voice.request_voice_fn(answer)
        connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
        connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
        connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to A DB with usage stats
        print("-----addded tokens to db--------")

        return answer

    elif cleaned_question.lower().startswith("db:") or "database_search" in agent_reply:
        query = cleaned_question.replace("db:", "").strip()
        messages.append({"role": "user", "content": query})
        answer = search_chroma_db(query)
        
        print("got answer from db" + answer)
        
        connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
        connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
        
        return answer

    elif "show_anime_list" in agent_reply or "show_manga_list" in agent_reply:
            
        content_type = "anime" if "anime" in agent_reply else "manga" 
        
        list_content, _ = anilist_api_requests.get_10_newest_entries("ANIME") if content_type == "anime" else anilist_api_requests.get_10_newest_entries("MANGA")  # assuming this method exists        
            
        question = f"Madrus: I will give you list of my 10 most recent watched/read {content_type} from site AniList. Here is this list:{list_content}. I want you to remember this because in next question I will ask you to update episodes/chapters of one of them."
        #print("question from user:" + question)
        messages.append({"role": "user", "content": question})

        # send to open ai for answer !!!!!!!! I WONT SEND IT BECOUSE I ALREADY GOT IT FROM reformatting
        answer = "Okay, I will remember it, Madrus. I'm waiting for your next question. Give it to me nyaa."
        answer_to_app = f"Here is your list of most recent anime/manga.{list_content}" # this goes 

      
        request_voice.request_voice_fn("Here is your list. *smile*") #request Azure TTS to for answer
           
        
        connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to Azure DB to user table    
        print("---------------------------------")

        
        return answer_to_app
        #content_type_mode = content_type # i need this so in next question i know what to update (anime or manga)
        
        #anilist_mode = True # entering anilist mode for next question to update anime/manga

        



    else: # normal question and answer mode
        # to database
        question = f"Madrus: {question}"
        print("question from user:" + question)
        messages.append({"role": "user", "content": question})
        
            # send to open ai for answer
        print("messages: " + str(messages))
        answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages) 
        print("ShiroAi-chan: " + answer)
         
        request_voice.request_voice_fn(answer) #request Azure TTS to for answer
        
        if profanity.contains_profanity(answer) == True:
            answer = profanity.censor(answer)     

        connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to DB to user table    
        connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
        connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to A DB with usage stats
        print("-----------saved to db ----------")
        
        return answer







if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.130", port=8000)
