from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import shutil
import os
import fitz  # PyMuPDF

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    print(f"Received file: {file.filename}")

    text = extract_text_from_pdf(file_path)
    print("[DEBUG] Extracted text length:", len(text))

    summary = summarize_text(text)
    print("[DEBUG] Summarization complete.")
    return {"message": f"Uploaded {file.filename} successfully.", "summary": summary}

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def summarize_text(text):
    print("[DEBUG] Starting summarization")
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",  # smaller model
        tokenizer="sshleifer/distilbart-cnn-12-6",
        framework="pt",
        model_kwargs={"force_download": True}  # force full clean download
    )

    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = [summarizer(chunk)[0]['summary_text'] for chunk in chunks]
    return " ".join(summaries)
