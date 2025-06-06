# NoteAI Prototype

A web-based tool to upload PDFs and extract their text using FastAPI + React.

## Tech Stack
- React.js (frontend)
- FastAPI (backend)
- PyMuPDF for PDF text extraction

## Setup

### Frontend and Backend
```bash
cd frontend
npm install
npm start

cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000


