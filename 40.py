from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
import uuid

app = FastAPI()

# In-memory storage for demonstration purposes
users = {}
api_keys = {}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    if username in users:
        user = users[username]
        if verify_password(password, user["hashed_password"]):
            return user
    return None

def create_access_token(data: dict):
    token = str(uuid.uuid4())
    api_keys[token] = data
    return token

async def get_current_user(token: Optional[str] = Depends(None)):
    if not token or token not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_keys[token]

@app.post("/register", response_model=Token)
async def register(user: UserCreate):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    users[user.username] = {"hashed_password": hashed_password}
    token = create_access_token({"sub": user.username})
    return Token(access_token=token, token_type="bearer")

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    user = authenticate_user(user.username, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return Token(access_token=token, token_type="bearer")

@app.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected endpoint", "user": current_user["sub"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)