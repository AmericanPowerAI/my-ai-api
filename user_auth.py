# user_auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import uuid

# In-memory database substitute
users_db: Dict[str, dict] = {}

# Config
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_router = APIRouter()

# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None
    tier: str = "free"  # 'free', 'pro', 'enterprise'

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(email: str):
    return users_db.get(email)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

# Routes
@auth_router.post("/register", response_model=Token)
def register(user: UserRegister):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "hashed_password": hashed_password,
        "phone": user.phone,
        "tier": user.tier,
    }
    access_token = create_access_token(data={"sub": user.email, "tier": user.tier})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login", response_model=Token)
def login(user: UserLogin):
    db_user = authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": db_user["email"], "tier": db_user["tier"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get current user tier
def get_current_user(token: str = Depends(lambda: None)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        user = get_user(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
