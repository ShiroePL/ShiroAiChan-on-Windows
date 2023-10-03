import string
from fastapi import FastAPI
from pydantic import BaseModel
from better_profanity import profanity
from starlette.responses import FileResponse
import base64
import connect_to_phpmyadmin
import chatgpt_api
import request_voice_tts as request_voice
app = FastAPI()

class Item(BaseModel):
    text: str

@app.post("/process")
async def process_text(item: Item):
    question = item.text
    name = "normal"
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database("normal")
    
    # to database
    question = f"Madrus: {question}"
    print("question from user:" + question)
    messages.append({"role": "user", "content": question})

        # send to open ai for answer
    print("messages: " + str(messages))
    answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages)        
    print("ShiroAi-chan: " + answer)
    
    if profanity.contains_profanity(answer) == True:
        answer = profanity.censor(answer)                    
   
    connect_to_phpmyadmin.insert_message_to_database(name, question, answer, messages) #insert to DB to user table    
    connect_to_phpmyadmin.add_pair_to_general_table(name, answer) #to general table with all  questions and answers
    connect_to_phpmyadmin.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to A DB with usage stats
    print("---------------------------------")

    request_voice.request_voice_fn(answer)
    
    

    # # Read the audio file and convert it to base64
    # with open("./kiki_hub/response.wav", "rb") as audio_file:
    #     encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')

    return {"result": answer}

@app.get("/get_audio")
async def get_audio():
    return FileResponse('./kiki_hub/response.wav', media_type='audio/wav')