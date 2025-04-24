# user_auth.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Fake database (replace with real DB like PostgreSQL)
users_db = {}

# JWT Secret (move this to an environment variable for production)
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    tier: str = "free"  # default tier: free

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    tier: Optional[str] = "free"

auth_router = APIRouter()

# Utilities
def fake_hash_password(password: str):
    return "hashed_" + password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Registration endpoint
@auth_router.post("/register")
def register(user: User):
    identifier = user.email or user.phone
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or phone required.")
    if identifier in users_db:
        raise HTTPException(status_code=400, detail="User already exists.")

    hashed_pw = fake_hash_password(user.password)
    users_db[identifier] = {"email": user.email, "phone": user.phone, "hashed_password": hashed_pw, "tier": user.tier}
    return {"message": "User registered successfully."}

# Login endpoint
@auth_router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="User not found.")
    if fake_hash_password(form_data.password) != user_dict["hashed_password"]:
        raise HTTPException(status_code=400, detail="Incorrect password.")

    access_token = create_access_token(
        data={"sub": form_data.username, "tier": user_dict["tier"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        tier: str = payload.get("tier")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(email=username, tier=tier)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Example protected route
@auth_router.get("/me")
def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return {"user": current_user.email, "tier": current_user.tier}
