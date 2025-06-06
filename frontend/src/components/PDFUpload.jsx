import React, { useState } from 'react';
import axios from 'axios';

function PDFUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a PDF to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setMessage(res.data.message);
      setSummary(res.data.summary);
    } catch (err) {
      console.error(err);
      setMessage("Upload failed. Check if the backend is running.");
    } finally {
        setLoading(false);
    }
  };

    return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: 'auto' }}>
      <h2>Upload a PDF</h2>
      <form onSubmit={handleUpload}>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" style={{ marginLeft: '1rem' }} disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {message && <p style={{ marginTop: '1rem' }}>{message}</p>}
      {loading && <p style={{ color: "gray" }}>Processing PDF and generating summary...</p>}

      {summary && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Extracted Summary:</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default PDFUpload;
