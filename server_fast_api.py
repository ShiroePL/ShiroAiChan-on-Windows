from fastapi import FastAPI
from pydantic import BaseModel
import shiro_on_android
app = FastAPI()



class QuestionWithUser(BaseModel):
    question: str
    username: str



@app.post("/question")
async def question(payload: QuestionWithUser):
    """
    A FastAPI endpoint to answer a question
    """
    question_text = payload.question
    username = payload.username

    answer = shiro_on_android.voice_control(question_text, username)
    # Process the question and username as needed
    done_answer = f"Hello, {username}! This is a test answer for your question: {answer}"
    return {"answer": done_answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.147.17.21", port=8000)
