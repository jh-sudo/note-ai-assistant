from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from functools import lru_cache
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util
import logging
import os
import fitz

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

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

# cache the model to avoid reloading
@lru_cache(maxsize=1)
def get_summarizer():
    logging.info("Loading summarization model...")
    return pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",  # smaller model for faster inference
        tokenizer="sshleifer/distilbart-cnn-12-6",
        framework="pt"
    )

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    logging.info(f"Received file: {file.filename}")

    text = extract_text_from_pdf(file_path)
    logging.info("[DEBUG] Extracted text length:", len(text))

    summary = summarize_text(text)
    logging.info("[DEBUG] Summarization complete.")
    return {"message": f"Uploaded {file.filename} successfully.", "summary": summary}

def extract_text_from_pdf(path):
    try:
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        logging.error(f"Error extracting PDF text: {e}")
        return ""

def summarize_text(text):
    logging.info("Starting summarization process...")
    summarizer = get_summarizer()

    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []

    for idx, chunk in enumerate(chunks):
        try:
            result = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            summaries.append(result)
            logging.info(f"Chunk {idx+1}/{len(chunks)} summarized.")
        except Exception as e:
            logging.error(f"Error summarizing chunk {idx+1}: {e}")

    return smart_paragraph_split(" ".join(summaries))


def smart_paragraph_split(summary_text):
    sentences = sent_tokenize(summary_text)
    if len(sentences) <= 1:
        return summary_text

    paragraphs = []
    current_paragraph = [sentences[0]]

    for i in range(1, len(sentences)):
        prev_emb = sentence_model.encode(current_paragraph[-1], convert_to_tensor=True)
        curr_emb = sentence_model.encode(sentences[i], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(prev_emb, curr_emb)

        if similarity < 0.7:
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = [sentences[i]]
        else:
            current_paragraph.append(sentences[i])

    paragraphs.append(" ".join(current_paragraph))
    return "\n\n".join(paragraphs)
