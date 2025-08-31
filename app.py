import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from pypdf import PdfReader
from werkzeug.utils import secure_filename
import easyocr
from transformers import pipeline
from keybert import KeyBERT

# Flask config
app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

# Models
summarizer = pipeline("summarization", model="t5-small")  
kw_model = KeyBERT()


def allowed_file(filename):
    # Check for allowed file type
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_pdf(file_path):
    # Pdf text ectractor
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        t = page.extract_text() or ""
        text += t
    return text


def extract_from_image(filepath):
    # Image text extractor
    reader = easyocr.Reader(['en'])
    results = reader.readtext(filepath, detail=0)
    return " ".join(results)


def summary_generate(text, length):
    # Summary Generator
    if not text.strip():
        return "Summarization Failed"

    if length == "short":
        minl, maxl = 30, 60
    elif length == "medium":
        minl, maxl = 80, 120
    else:  # long
        minl, maxl = 150, 200

    max_chunk = 1000
    chunks = [text[i: i + max_chunk] for i in range(0, len(text), max_chunk)]
    summary = ""

    for chunk in chunks:
        result = summarizer(chunk, max_length=maxl, min_length=minl, do_sample=False)
        summary += result[0]['summary_text'] + " "

    return summary.strip()


def extract_keywords(text, top_n=8):
    if not text.strip():
        return []
    keywords = kw_model.extract_keywords(text, top_n=top_n, stop_words="english")
    return [kw for kw, score in keywords]


def highlight_text(text, keywords):
    """Highlight keywords inside summary text"""
    if not keywords or not text:
        return text
    for kw in keywords:
        text = text.replace(kw, f"<span class='highlight'>{kw}</span>")
    return text

# Routings
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pdf", methods=["GET", "POST"])
def extract_pdf():
    if request.method == "POST":
        file = request.files.get("file")
        summary_length = request.form.get("summary_length")

        if not file or file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename) and file.filename.lower().endswith(".pdf"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            text = extract_text_pdf(filepath)

            summary, keywords, highlighted_summary = None, None, None
            if summary_length:
                summary = summary_generate(text, summary_length)
                keywords = extract_keywords(summary, top_n=8)
                highlighted_summary = highlight_text(summary, keywords)

            return render_template(
                "ext_pdf.html",
                filename=filename,
                extracted_text=text,
                summary=highlighted_summary,
                summary_length=summary_length,
                keywords=keywords
            )
        else:
            flash("Invalid file. Please upload a PDF.")
            return redirect(request.url)

    return render_template("ext_pdf.html")


@app.route("/image", methods=["GET", "POST"])
def extract_img():
    if request.method == "POST":
        file = request.files.get("file")
        summary_length = request.form.get("summary_length")

        if not file or file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename) and file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            text = extract_from_image(filepath)

            summary, keywords, highlighted_summary = None, None, None
            if summary_length:
                summary = summary_generate(text, summary_length)
                keywords = extract_keywords(summary, top_n=8)
                highlighted_summary = highlight_text(summary, keywords)

            return render_template(
                "ext_img.html",
                filename=filename,
                extracted_text=text,
                summary=highlighted_summary,
                summary_length=summary_length,
                keywords=keywords
            )
        else:
            flash("Invalid file. Please upload an Image (png/jpg/jpeg).")
            return redirect(request.url)

    return render_template("ext_img.html")


if __name__ == "__main__":
    app.run(debug=True)
