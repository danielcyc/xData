import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)

def test_successful_transcription():
    with open("tests/audio_samples/Sample 1.mp3", "rb") as f:
        response = client.post("/transcribe", files={"file": ("Sample 1.mp3", f, "audio/mpeg")})

    assert response.status_code == 200
    assert "filename" in response.json()
    assert "transcription" in response.json()
    assert response.json()["transcription"] != ""

def test_missing_audio_file():
    response = client.post("/transcribe")
    
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "file" in response.json()["detail"][0]["loc"]

def test_invalid_audio_file():
    with open("tests/Test Text File.txt", "rb") as f:
        response = client.post("/transcribe", files={"file": ("Test Text File.txt", f, "text/plain")})

    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Error loading audio file" in response.json()["detail"]
