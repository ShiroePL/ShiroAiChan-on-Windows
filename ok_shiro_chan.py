import speech_recognition as sr
import pyttsx3
import time 
import kiki_hub.request_whisper as request_whisper
from playsound import playsound
import base64
import requests
import os
import wave
import pyaudio
import connect_to_azuredb
import pyodbc
import api_keys
import winsound
import asyncio
import subprocess

# Initialize the text to speech engine 
engine=pyttsx3.init()

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
    print("text from audio question: " + question)
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



def main():
    #input your name
    print("What is your name?: ")
    name = input()

    
    while True:
        #Wait for user to say "pathfinder"
        print("Say 'pathfinder' to start recording your question")
        # with sr.Microphone() as source:
        #     recognizer = sr.Recognizer()
        #     audio = recognizer.listen(source)
        #     alias = "alias"
        #     transcribed = f"./kiki_hub/{alias}.wav"
        #     with open(transcribed, "wb") as f:
        #         f.write(audio.get_wav_data())
        #     f.close()  
        try:
            #transcription = transcribe_audio_question(alias) #make transcription from alias file
            #if transcription.rstrip('.,?!').replace(' ', '').lower() == "pathfinder":
                    #record audio
            question_file = "question"
            filename = f"./kiki_hub/{question_file}.wav"
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
            #transcript audio to text 
            text = transcribe_audio_question(question_file)
            if text:
                print(f"you said {text}")
                play_audio_fn(question_file)
                    #Generate the response
                    # response = open_ai_api.send_to_openai(text)
                    # print(f"chat gpt 3 say {response}")
                        
                    #read response using GPT3
                    #speak_text(response)
        except Exception as e:
            print("An error occurred: {}".format(e))

if __name__ == "__main__":
    main()
