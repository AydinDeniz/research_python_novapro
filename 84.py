# Prompt 84

from fastapi import FastAPI, File, UploadFile
import whisper
import io
from pydub import AudioSegment
import psycopg2
from psycopg2 import sql

app = FastAPI()

# Initialize Whisper model
model = whisper.load_model("base")

# Database connection
conn = psycopg2.connect(database="yourdb", user="youruser", password="yourpassword", host="localhost", port="5432")
cur = conn.cursor()

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save the uploaded file
    audio_data = await file.read()
    audio = AudioSegment.from_file(io.BytesIO(audio_data))
    
    # Transcribe audio
    result = model.transcribe(audio)
    transcript = result["text"]
    
    # Perform speaker diarization (simplified example)
    speakers = result["segments"]
    
    # Store in database
    insert_query = sql.SQL("INSERT INTO transcripts (transcript, timestamp, speaker) VALUES (%s, %s, %s)")
    for segment in speakers:
        cur.execute(insert_query, (transcript, segment["start"], segment["speaker"]))
    
    conn.commit()
    
    return {"transcript": transcript, "speakers": speakers}