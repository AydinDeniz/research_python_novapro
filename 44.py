from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import json
import re

app = FastAPI()

# Define sensitive headers and tokens to exclude from logs
SENSITIVE_HEADERS = {"authorization", "cookie"}
SENSITIVE_TOKEN_PATTERN = re.compile(r"(?i)(apikey|token|bearer|secret|password|signature)")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log incoming request
        request_id = request.headers.get("x-request-id", "unknown")
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        headers = {k: v for k, v in request.headers.items() if k.lower() not in SENSITIVE_HEADERS}
        
        log_entry = {
            "request_id": request_id,
            "client_ip": client_ip,
            "method": method,
            "url": url,
            "headers": headers,
            "timestamp": start_time,
        }
        
        print(json.dumps(log_entry, indent=2))
        
        # Call the next middleware or the route handler
        response: Response = await call_next(request)
        
        # Log outgoing response
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # Exclude sensitive headers from response headers
        response_headers = {k: v for k, v in dict(response.headers).items() if k.lower() not in SENSITIVE_HEADERS}
        
        log_entry = {
            "request_id": request_id,
            "client_ip": client_ip,
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_headers": response_headers,
            "process_time": process_time,
            "timestamp": time.time(),
        }
        
        print(json.dumps(log_entry, indent=2))
        
        return response

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id")
    if not request_id:
        request_id = "unknown"
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response

app.add_middleware(LoggingMiddleware)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)