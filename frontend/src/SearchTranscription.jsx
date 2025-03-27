import React, { useState } from "react";
import axios from "axios";

const SearchTranscription = () => {
  const [filename, setFilename] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!filename) return;

    try {
      const response = await axios.get(
        `http://localhost:8000/search?filename=${filename}`
      );
      setResult(response.data);
      setError(null);
    } catch (err) {
      setError("File not found", err);
      setResult(null);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter filename"
        value={filename}
        onChange={(e) => setFilename(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>

      {result && (
        <div>
          <h3>Transcription for {result.filename}</h3>
          <p>{result.transcription}</p>
          <small>{result.timestamp}</small>
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default SearchTranscription;
