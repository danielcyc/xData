import { useState, useEffect } from "react";
import React from "react";
import FileUpload from "./FileUpload";
import TranscriptionList from "./TranscriptionList";
import SearchTranscription from "./SearchTranscription";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.status);
        console.log(data);
      })
      .catch((err) => console.error("Error fetching data:", err));
    console.log(message);
  }, []);

  return (
    <>
      <h1>xData</h1>
      <div>Backend API Status: {message} </div>
      <div>
        <h2>Upload your file</h2>
        <FileUpload />
      </div>
      <div>
        <h2>Search Transcriptions</h2>
        <SearchTranscription />
      </div>
      <div>
        <h2>All Transcriptions</h2>
        <TranscriptionList />
      </div>
    </>
  );
}

export default App;
