# RAG with PDF Review

## Expected Solution
- The user uploads a **PDF document**.
- The system processes the **PDF into a vector database**.
- The user asks a question related to the PDF.
- The system **retrieves one or more relevant sections** and highlights them in the **PDF viewer**.
- The **PDF viewer** should support **highlighting retrieved text** based on **line number indexing**.
- Consider using **PDFValue** and **PDFViewerProps** for rendering highlights.

## Expected Tools
- **PDF Parsing:** OpenAI’s **file search assistant** (preferred for minimal engineering effort).
- **Vector DB:** FAISS for embedding-based search.
- **Embedding Model:** OpenAI’s embedding API
- **PDF Viewer:** **pdf.js** or another library that supports **text highlighting**.

## Deliverable
- **Self-contained open-source code** with:
  - A **Python class** to:
    - **Load and parse** the PDF.
    - **Process queries** and retrieve relevant content.
  - **Vector DB setup** for efficient document indexing.
  - A **frontend PDF viewer** supporting text highlights.
  - A **README file** with:
    - Dependency installation instructions.
    - Clear usage examples.
