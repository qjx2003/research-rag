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
