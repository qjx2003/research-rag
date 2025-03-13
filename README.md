RAG with PDF Review

Overview
This project implements a Retrieval-Augmented Generation (RAG) system that enables users to upload PDFs, query them, and retrieve relevant sections. The system highlights the most relevant paragraph in the PDF based on the user’s query.

Features
PDF Upload & Processing: Converts PDFs into a searchable vector database.
Query Processing: Retrieves the most relevant content from the PDF based on user queries.
Efficient Text Highlighting: Finds the single most relevant paragraph instead of scattered highlights.
Vector Search: Uses OpenAI's file search assistant and FAISS for fast retrieval.
PDF Viewer Support: Highlights retrieved content directly in the PDF.

Technologies Used
PDF Parsing: PyMuPDF (fitz) for extracting and highlighting text.
Vector Database: OpenAI’s vector store and FAISS.
Embedding Model: OpenAI's embedding API for query processing.
Text Matching: Uses TF-IDF + Cosine Similarity and RapidFuzz for best paragraph matching.

## Installation
Follow these steps to set up and run the project:
### 1. Install Dependencies
```sh
pip install openai pymupdf scikit-learn numpy rapidfuzz

### 2. Set Up OpenAI API Key & Run the Script
```sh
For Linux/macOS:
export OPENAI_API_KEY="your-api-key"
python pdf_rag.py
For Windows Command Prompt:
set OPENAI_API_KEY=your-api-key
python pdf_rag.py
For Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key"
python pdf_rag.py

Usage
1.Upload a PDF.
2.Ask a question related to the PDF.
3.Retrieve and highlight the most relevant paragraph.
4.View the highlighted PDF (highlighted_output.pdf).

File Structure
```sh
pdf-rag/
│── pdf_rag.py              # Main script for PDF processing and querying
│── example.pdf             # Sample PDF file
│── highlighted_output.pdf  # Output with highlights
│── highlight_data.json     # Stores highlight metadata
│── README.md               # Project documentation

Future Improvements
1.Multi-page document search.
2.Faster indexing for large PDFs.
3.Different highlight colors for various queries.

