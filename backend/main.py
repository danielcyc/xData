from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sqlite3
from datetime import datetime
import torchaudio
from transformers import pipeline

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_FILE = "transcriptions.db"

# Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model
whisper = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")

# Initialize SQLite Database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transcriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT UNIQUE,
                        transcription TEXT,
                        timestamp TEXT)''')
        conn.commit()
    print("db inited")

init_db()

@app.get("/")
def read_root():
    return health_check()

# Healthcheck Endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Search db for duplicate name and append number for copy
def get_unique_filename(filename: str) -> str:
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = f"{base_name}{ext}"
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        while True:
            c.execute("SELECT COUNT(*) FROM transcriptions WHERE filename = ?", (new_filename,))
            if c.fetchone()[0] == 0:
                break
            new_filename = f"{base_name}_{counter}{ext}"
            counter += 1
    
    return new_filename

# Transcribe Audio Endpoint
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    new_filename = get_unique_filename(file.filename)

    # Load audio
    audio_tensor, rate = torchaudio.load(file.file)
    transcription = whisper(audio_tensor[0].numpy(), sampling_rate=rate)["text"]
    
    # Save to db
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO transcriptions (filename, transcription, timestamp) VALUES (?, ?, ?)",
                  (new_filename, transcription, datetime.now().isoformat()))
        conn.commit()
    
    return {"filename": new_filename, "transcription": transcription}

# Retrieve All Transcriptions
@app.get("/transcriptions")
def get_transcriptions():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT filename, transcription, timestamp FROM transcriptions")
        data = [{"filename": row[0], "transcription": row[1], "timestamp": row[2]} for row in c.fetchall()]
    return JSONResponse(content=data)

# Search Transcriptions by Filename
@app.get("/search")
def search_transcriptions(filename: str):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT filename, transcription, timestamp FROM transcriptions WHERE filename = ?", (filename,))
        row = c.fetchone()
    
    if row:
        return {"filename": row[0], "transcription": row[1], "timestamp": row[2]}
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
