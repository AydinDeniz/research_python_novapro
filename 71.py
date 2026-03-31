from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import subprocess
import asyncio
import aiofiles
import boto3
import os

app = FastAPI()

s3_client = boto3.client("s3", aws_access_key_id="YOUR_ACCESS_KEY", aws_secret_access_key="YOUR_SECRET_KEY", region_name="YOUR_REGION")

class VideoTranscodeRequest(BaseModel):
    video_path: str
    output_format: str

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Video Transcoding</title>
    </head>
    <body>
        <h1>Video Transcoding</h1>
        <div id="log"></div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var log = document.getElementById("log");
                log.innerHTML += event.data + "<br>";
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.post("/transcode")
async def transcode_video(request: VideoTranscodeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(transcode, request.video_path, request.output_format)
    return {"message": "Transcoding started"}

async def transcode(video_path, output_format):
    output_file = f"output.{output_format}"
    command = f"ffmpeg -i {video_path} -c:v libx264 -c:a aac -strict experimental {output_file}"
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        while True:
            line = await process.stderr.readline()
            if line:
                await websocket.send(line.decode())
            if process.returncode is not None:
                break

    retcode = await process.wait()
    if retcode == 0:
        await upload_to_s3(output_file)
        os.remove(output_file)
    else:
        print(f"Error occurred while transcoding: {retcode}")

async def upload_to_s3(file_path):
    bucket_name = "your-bucket-name"
    async with aiofiles.open(file_path, "rb") as f:
        file_content = await f.read()
    s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=file_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)