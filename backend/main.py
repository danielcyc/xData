import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sqlite3
from datetime import datetime
import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

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

# Load Whisper model and processor
model_name = "openai/whisper-tiny"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# Set the model to eval mode
model.eval()

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

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    new_filename = get_unique_filename(file.filename)
    audio_data = await file.read()
    # Use BytesIO to turn the bytes into a file-like object for librosa
    audio_io = io.BytesIO(audio_data)
    # Load audio file using librosa
    try:
        # Load audio at 16kHz sample rate for Whisper compatibility
        audio, rate = librosa.load(audio_io, sr=16000)  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading audio file: {str(e)}")
    
    # Define chunk duration (in seconds)
    chunk_duration = 30  # seconds
    chunk_length = chunk_duration * 16000  # 16kHz sample rate

    # Split the audio into chunks
    num_chunks = len(audio) // chunk_length
    chunks = [audio[i * chunk_length: (i + 1) * chunk_length] for i in range(num_chunks)]

    # If there's leftover audio, add it as another chunk
    if len(audio) % chunk_length != 0:
        chunks.append(audio[num_chunks * chunk_length:])

    # List to store transcriptions for all chunks
    transcriptions = []

    # Process each chunk
    for chunk in chunks:
        try:
            # Process the chunk with Whisper
            inputs = processor(chunk, return_tensors="pt", sampling_rate=16000)
            input_features = inputs["input_features"]

            # Generate transcription for the chunk
            with torch.no_grad():
                generated_ids = model.generate(input_features)

            # Decode the transcription
            transcription = processor.decode(generated_ids[0], skip_special_tokens=True)
            transcriptions.append(transcription)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error transcribing audio: {str(e)}")

    # Join transcriptions from all chunks
    full_transcription = " ".join(transcriptions)

    # Save to db
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO transcriptions (filename, transcription, timestamp) VALUES (?, ?, ?)",
                  (new_filename, full_transcription, datetime.now().isoformat()))
        conn.commit()

    return {"filename": new_filename, "transcription": full_transcription}

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
