import React, { useState } from 'react';
import axios from 'axios';

function PDFUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [extractedText, setExtractedText] = useState("");  // 🆕 Step 1

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setMessage(res.data.message);
      setExtractedText(res.data.extracted_text);  // 🆕 Step 2
    } catch (err) {
      setMessage("Upload failed.");
      setExtractedText("");  // Clear on failure
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload a PDF</h2>
      <form onSubmit={handleUpload}>
        <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files[0])} />
        <button type="submit">Upload</button>
      </form>

      {message && <p>{message}</p>}

      {/* 🆕 Step 3: Show extracted text */}
      {extractedText && (
        <div>
          <h3>Extracted Text:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', textAlign: 'left' }}>
            {extractedText}
          </pre>
        </div>
      )}
    </div>
  );
}

export default PDFUpload;
