from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from model import ai_model
from user_auth import auth_router

app = FastAPI()

# Allow CORS from any domain (safe for dev, change "*" to your domain later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret API keys for devs/engineers
VALID_API_KEYS = {"your-secret-key"}

# Only check if one is provided
def validate_api_key(api_key: Optional[str]):
    if api_key is not None and api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

# Request schemas with optional api_key
class LearnRequest(BaseModel):
    fact: str
    api_key: Optional[str] = None

class TrainRequest(BaseModel):
    text: str
    api_key: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str
    api_key: Optional[str] = None

# Routes
@app.get("/")
def read_root():
    return {"message": "Nero AI is running."}

@app.post("/learn")
def learn_fact(req: LearnRequest):
    validate_api_key(req.api_key)
    ai_model.learn(req.fact)
    return {"status": "Learned", "fact": req.fact}

@app.post("/train")
def train_model(req: TrainRequest):
    validate_api_key(req.api_key)
    ai_model.train(req.text)
    return {"status": "Trained", "text": req.text}

@app.post("/ask")
def ask_question(req: QuestionRequest):
    validate_api_key(req.api_key)
    answer = ai_model.answer(req.question)
    return {"answer": answer}

# Include the auth router from user_auth.py
app.include_router(auth_router)
