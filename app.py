from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model import ai_model

app = FastAPI()

# Allow CORS from any domain (safe for dev, change "*" to your domain later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example secret API key (change this to your real one or load from env)
VALID_API_KEYS = {"your-secret-key"}

def validate_api_key(api_key: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

# Request schemas
class LearnRequest(BaseModel):
    fact: str
    api_key: str

class TrainRequest(BaseModel):
    text: str
    api_key: str

class QuestionRequest(BaseModel):
    question: str
    api_key: str

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
