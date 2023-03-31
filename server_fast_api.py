from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Numbers(BaseModel):
    a: int
    b: int
class Question(BaseModel):
    question: str


@app.post("/multiply")
async def multiply_numbers(numbers: Numbers):
    """
    A FastAPI endpoint to multiply two numbers
    """
    result = numbers.a * numbers.b
    print(f"Received numbers: a = {numbers.a}, b = {numbers.b}")
    print(f"Result: {result}")
    return {"result": f"twoja liczba{result}"}



@app.post("/question")
async def question(question: Question):
    """
    A FastAPI endpoint to answer a question
    """
    answer = "it worked"
    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.147.17.21", port=8000)
