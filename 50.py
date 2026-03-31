from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
import time

app = FastAPI()

# In-memory storage for failed attempts (for demonstration purposes)
failed_attempts: Dict[str, int] = {}
blocked_ips: Dict[str, float] = {}

class LoginRequest(BaseModel):
    username: str
    password: str

def is_blocked(ip: str) -> bool:
    if ip in blocked_ips and time.time() < blocked_ips[ip]:
        return True
    return False

def block_ip(ip: str):
    blocked_ips[ip] = time.time() + 600  # Block for 10 minutes

def track_failed_attempt(ip: str):
    if ip in failed_attempts:
        failed_attempts[ip] += 1
        if failed_attempts[ip] >= 5:
            block_ip(ip)
            del failed_attempts[ip]
    else:
        failed_attempts[ip] = 1

async def check_blocked_ip(ip: str = Depends(lambda: None)):
    if is_blocked(ip):
        raise HTTPException(status_code=403, detail="Too many failed attempts. Please try again later.")

@app.post("/login")
async def login(login_request: LoginRequest, ip: str = Depends(lambda: None)):
    if is_blocked(ip):
        raise HTTPException(status_code=403, detail="Too many failed attempts. Please try again later.")
    
    # Simulate authentication (replace with actual authentication logic)
    if login_request.username == "user" and login_request.password == "password":
        return {"message": "Login successful"}
    else:
        track_failed_attempt(ip)
        raise HTTPException(status_code=401, detail="Invalid credentials")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)