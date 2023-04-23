from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

import connect_to_phpmyadmin
import shiro_on_android
app = FastAPI()



class QuestionWithUser(BaseModel):
    question: str
    username: str

class ChatMessage(BaseModel):
    role: str
    content: str



@app.get("/chat_history/{name}")
async def get_chat_history(name: str):
    messages = connect_to_phpmyadmin.retrieve_chat_history_from_database(name)
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

    answer = shiro_on_android.voice_control(question_text, username)
    # Process the question and username as needed
    done_answer = f" {answer}"
    return {"answer": done_answer}

if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="10.147.17.21", port=8000)
