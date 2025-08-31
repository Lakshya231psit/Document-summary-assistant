Document Summary Assistant

A simple web app to upload documents (PDFs or images) and generate summaries in different lengths (short, medium, long). It uses OCR for scanned images and AI models for text summarization.

Features

Upload PDFs and images

Extract text using PDF parser or OCR

Generate short, medium, long summaries

Highlight keywords and main ideas

Simple, mobile-friendly interface

Tech Used

Python (Flask)

pypdf – extract text from PDFs

easyocr / pytesseract – read text from images

transformers – AI text summarization

Bootstrap – frontend styling

How to run?

1-> Open the code in code editor

2-> Install requirements

	command to install -> pip install -r requirements.txt

3-> Open terminal directory 
	
	command to execute -> python app.py

4-> Open Browser

	type url -> http://127.0.0.1:5000/
