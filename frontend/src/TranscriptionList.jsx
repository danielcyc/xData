import React, { useState, useEffect } from "react";
import axios from "axios";

const TranscriptionList = () => {
  const [transcriptions, setTranscriptions] = useState([]);

  useEffect(() => {
    const fetchTranscriptions = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/transcriptions"
        );
        setTranscriptions(response.data);
      } catch (error) {
        console.error("Error fetching transcriptions:", error);
      }
    };

    fetchTranscriptions();
  }, []);

  return (
    <div>
      <h3>Transcriptions</h3>
      <ul>
        {transcriptions.map((transcription) => (
          <li key={transcription.filename}>
            <strong>{transcription.filename}</strong>
            <p>{transcription.transcription}</p>
            <small>{transcription.timestamp}</small>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TranscriptionList;
