from fastapi import FastAPI, Request
from model import ai_model

app = FastAPI()

@app.post("/train")
async def train_model(request: Request):
    data = await request.json()
    ai_model.train(data["text"])
    return {"status": "trained"}

@app.get("/ask")
def ask(question: str):
    answer = ai_model.answer(question)
    return {"question": question, "answer": answer}

@app.post("/learn")
async def learn_new(request: Request):
    data = await request.json()
    ai_model.learn(data["fact"])
    return {"status": "learned"}
