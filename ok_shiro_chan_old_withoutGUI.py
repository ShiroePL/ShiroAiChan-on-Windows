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
import redis

redis_client = redis.Redis(host='localhost', port=6379)


    

# Initialize the question to speech engine 
engine=pyttsx3.init()
conn = None
transcription = ""

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



def main():
    #input your name
    print("say 'exit program' to exit the program")
    print("What is your name?: ")
    name = input()
    print("Do you want to reset your chat history? (yes/no):")
    choice = input()
    if choice =="yes":
        connect_to_phpmyadmin.reset_chat_history(name)
        
    connect_to_phpmyadmin.check_user_in_database(name)
    
    while True:
        messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
        #Wait for user to say "pathfinder"
        print("Say 'pathfinder' to start a conversation")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            alias = "alias"
            transcribed = f"./kiki_hub/{alias}.wav"
            with open(transcribed, "wb") as f:
                f.write(audio.get_wav_data())
            f.close()  
            try:
                transcription = transcribe_audio_question(alias) #make transcription from alias file
                redis_client.set('mykey1', transcription)
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
                        
                


            except Exception as e:
                print("An error occurred: {}".format(e))

if __name__ == "__main__":
    main()
