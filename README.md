# AI Invoice Extractor

An AI-powered invoice processing and finance assistant built using Python, FastAPI, PostgreSQL, Gemini AI, and Retrieval-Augmented Generation (RAG).

## Project Overview

AI Invoice Extractor automates invoice data extraction from PDF and DOCX documents.

It uses Gemini AI to extract structured invoice information, stores invoice records in PostgreSQL, generates text embeddings, and enables semantic search and question answering using RAG.

## Technology Stack

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Gemini API
- PyMuPDF
- python-docx
- pgvector
- Pydantic
- Uvicorn

## Key Features

- Vendor management
- Invoice creation and management
- Payment management
- PDF text extraction
- DOCX text extraction
- AI-based invoice field extraction
- Automatic invoice storage in PostgreSQL
- Text preprocessing and chunking
- Embedding generation
- Vector storage using pgvector
- Semantic search
- Invoice question answering using RAG
- Duplicate invoice validation

## Project Structure

```text
AI-Invoice-Extractor/
├── app/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── main.py
│   └── ai-service.py
├── test_ai_extractor.py
├── test_chunker.py
├── test_db.py
├── test_docx_extraction.py
├── test_embedding_storage.py
├── test_embedding.py
├── test_pdf_pages.py
├── test_preprocessor.py
├── test_rag.py
├── test_semantic_chunker.py
├── test_semantic_search.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd AI-Invoice-Extractor
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root.

Add the following configuration:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/finance_ai
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Replace the database credentials and API key with your own values.

**Never upload your `.env` file or API keys to GitHub.**

## Database Setup

1. Install PostgreSQL.
2. Create a database named `finance_ai`.
3. Enable the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The application uses SQLAlchemy to manage database connections and models.

## Run the Application

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application welcome |
| GET | `/health` | Health check |
| POST | `/vendors` | Create vendor |
| GET | `/vendors` | Get all vendors |
| GET | `/vendors/{vendor_id}` | Get vendor by ID |
| POST | `/invoices` | Create invoice |
| GET | `/invoices` | Get all invoices |
| GET | `/invoices/{invoice_id}` | Get invoice by ID |
| POST | `/payments` | Create payment |
| GET | `/payments` | Get all payments |
| GET | `/invoices/{invoice_id}/summary` | Invoice payment summary |
| POST | `/invoices/extract-text` | Extract PDF text |
| POST | `/invoices/extract` | Extract invoice fields |
| POST | `/invoices/extract-and-save` | Extract and save PDF/DOCX invoices |
| POST | `/invoices/semantic-search` | Search invoice embeddings |
| POST | `/invoices/ask` | Ask questions using RAG |

## Example API Requests

### Invoice Semantic Search

```json
{
  "question": "Find invoices with GST amount",
  "limit": 5
}
```

### Ask Invoice Questions Using RAG

```json
{
  "question": "What is the total amount of invoice INV-1005?"
}
```

### Upload Invoice

Use the `/invoices/extract-and-save` endpoint in Swagger.

Select a PDF or DOCX invoice and execute the request.

## RAG Workflow

1. Extract text from invoice documents.
2. Preprocess the extracted text.
3. Divide text into smaller chunks.
4. Generate embeddings using Gemini.
5. Store embeddings in PostgreSQL using pgvector.
6. Convert the user's question into an embedding.
7. Retrieve relevant invoice chunks using semantic search.
8. Send retrieved context to Gemini.
9. Generate an answer based on the retrieved invoice information.

## Error Handling

The application includes validation for:

- Unsupported file formats
- Empty files
- Invalid PDF documents
- Missing invoice information
- Duplicate invoice numbers
- Unknown vendors

## Future Enhancements

- Hybrid search using BM25 and vector search
- RAG source citations and page references
- Improved retrieval accuracy
- Automated evaluation of RAG responses
- Conversational invoice assistant

## Author

AI-Invoice-Extractor – Personal GenAI Engineering Project.
