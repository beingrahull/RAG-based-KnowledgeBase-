# RAG KBEng

A production-shaped Retrieval-Augmented Generation backend for question-answering over private PDF documents. Built with FastAPI, MongoDB, Pinecone, and Google Gemini.

The system ingests PDFs, chunks and embeds them, stores vectors in Pinecone, and answers user questions by retrieving the most relevant chunks and constraining a large language model to answer only from that retrieved context.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [RAG Pipeline](#rag-pipeline)
- [Testing](#testing)
- [Evaluation](#evaluation)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Overview

RAG KBEng answers questions grounded in a private corpus of documents. It does not rely on the LLM's general knowledge. Every answer is derived from retrieved chunks of the user's own PDFs, with citations to the source chunks.

Core capabilities:

- **Authentication** — JWT sessions issued as HTTP-only cookies.
- **Document ingestion** — PDF upload, text extraction, chunking, embedding, and vector storage.
- **Semantic retrieval** — cosine similarity search over embedded chunks.
- **Grounded generation** — LLM answers with strict JSON output and source citations.
- **Access control** — users only see and query their own documents.

---

## Architecture

```
                    ┌───────────────────────────┐
                    │        Client             │
                    │  (browser / Postman / API)│
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      FastAPI (uvicorn)    │
                    │   app/main.py             │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼──────────────────────────┐
        │                         │                          │
┌───────▼────────┐      ┌─────────▼──────────┐     ┌─────────▼────────┐
│   Auth Router  │      │ Documents Router   │     │   Query Router   │
│ /api/auth/*    │      │ /api/documents/*   │     │   /api/query     │
└───────┬────────┘      └─────────┬──────────┘     └─────────┬────────┘
        │                         │                          │
        ▼                         ▼                          ▼
┌───────────────┐      ┌──────────────────┐        ┌───────────────────┐
│ user_service  │      │ document_service │        │ retrieval_service │
│ security util │      │ ingestion_service│        │ prompt_service    │
└───────┬───────┘      └─────────┬────────┘        │ llm_service       │
        │                        │                 └─────────┬─────────┘
        │                        │                           │
        ▼                        ▼                           ▼
   ┌─────────┐         ┌──────────────────┐         ┌───────────────────┐
   │ MongoDB │         │ Local disk (PDF) │         │ Gemini Embeddings │
   │ (users, │         │ + MongoDB meta   │         │ Pinecone (vectors)│
   │  docs)  │         │ + Pinecone vecs  │         │ Gemini LLM        │
   └─────────┘         └──────────────────┘         └───────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Runtime | Python 3.12 | Language |
| Web framework | FastAPI | HTTP API |
| ASGI server | Uvicorn | Production server |
| Validation | Pydantic v2 | Request/response schemas |
| Config | pydantic-settings | `.env` loading and validation |
| Database | MongoDB Atlas | Document storage |
| ODM | Beanie | Async MongoDB modeling |
| Driver | PyMongo (AsyncMongoClient) | Async MongoDB connectivity |
| Auth | PyJWT | JWT signing and verification |
| Hashing | bcrypt | Password hashing |
| PDF parsing | pypdf | Text extraction |
| Chunking | langchain-text-splitters | Recursive text splitting |
| Embeddings | Google Gemini (`gemini-embedding-2`) | 1536-dim vectors |
| LLM | Google Gemini (`gemini-3.6-flash`) | Answer generation |
| Vector database | Pinecone | Cosine similarity search |
| Testing | pytest, pytest-asyncio, httpx | Test suite |

---

## Project Structure

```
Backend/
├── app/
│   ├── main.py                     FastAPI app and router mounting
│   ├── config.py                   Settings loaded from .env
│   ├── database.py                 Beanie initialization
│   ├── dependencies.py             Auth dependency (get_current_user)
│   ├── routers/
│   │   ├── auth.py                 Register, login, /me, logout
│   │   ├── documents.py            Upload, list, status
│   │   └── query.py                RAG query endpoint
│   ├── services/
│   │   ├── user_service.py         Register, authenticate, find_by_email
│   │   ├── document_service.py     Save uploads, list documents
│   │   ├── ingestion_service.py    Full ingestion pipeline
│   │   ├── chunking_service.py     Recursive text splitting
│   │   ├── embedding_service.py    Gemini batch embeddings with retries
│   │   ├── vector_store_service.py Pinecone upsert and query
│   │   ├── retrieval_service.py    Question → top-K chunks
│   │   ├── prompt_service.py       Build the RAG prompt
│   │   └── llm_service.py          Gemini answer generation + JSON parsing
│   ├── schemas/
│   │   ├── auth.py                 Register/Login request & response models
│   │   ├── document.py             DocumentPublic, UploadResponse
│   │   ├── query.py                QueryRequest, QueryResponse, SourceRef
│   │   └── llm_output.py           LLMAnswer — the LLM JSON contract
│   ├── models/
│   │   ├── user.py                 User document (Beanie)
│   │   ├── document.py             UploadedDocument document
│   │   └── chunk.py                Chunk document
│   └── utils/
│       ├── security.py             hash_password, verify_password, JWT
│       └── pdf_parser.py           extract_text_from_pdf
├── tests/
│   ├── conftest.py                 Async client fixture with lifespan
│   ├── test_auth.py                Register and login tests
│   ├── test_documents.py           Upload and listing tests
│   └── test_query.py               Query endpoint tests
├── eval/
│   ├── datasets/qa.jsonl           Golden question set
│   ├── metrics/recall.py           Recall@K implementation
│   └── runner.py                   Evaluation runner
├── uploads/                        Uploaded PDF files (gitignored)
├── pyproject.toml                  Project metadata, deps, pytest config
├── .env                            Local secrets (gitignored)
└── .env.example                    Template for .env
```

---

## Setup

### Prerequisites

- Python 3.12 or higher
- A MongoDB Atlas cluster (or local MongoDB)
- A Pinecone account with an index created
- A Google Gemini API key

### Install

```bash
git clone <repository-url>
cd Backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### Pinecone index

Create an index named `rag-kbeng` with:

- **Dimension:** 1536
- **Metric:** cosine
- **Cloud:** AWS us-east-1 (or your preferred region)

### MongoDB

Any Atlas cluster works. The free M0 tier is sufficient for development. Whitelist your IP under **Network Access**.

---

## Environment Variables

Create a `.env` file at the backend root:

```env
# Application
APP_NAME="RAG KBEng"
ENV=development
PORT=4000

# Database
MONGO_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/
MONGO_DB_NAME=rag_kbeng

# Auth
JWT_SECRET=<generate-with-secrets.token_urlsafe(48)>
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=10080

# Google Gemini
GEMINI_API_KEY=<your-gemini-api-key>
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIM=1536

# Pinecone
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=rag-kbeng

# RAG tuning
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K_RETRIEVE=5
```

Generate a strong secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## Running the Application

```bash
python run.py
```

Expected startup output:

```
Connected to MongoDB: rag_kbeng
Server on http://127.0.0.1:4000
Docs on http://127.0.0.1:4000/docs
INFO:     Uvicorn running on http://127.0.0.1:4000
```

Interactive API documentation is available at `/docs`.

---

## API Reference

Base URL: `http://127.0.0.1:4000`

### Authentication

#### Register

```
POST /api/auth/register
Content-Type: application/json
```

Request:

```json
{
  "name": "Rahul",
  "email": "rahul@example.com",
  "password": "test1234"
}
```

Response `201`:

```json
{
  "message": "Account Registered",
  "user": {
    "id": "671abc...",
    "name": "Rahul",
    "email": "rahul@example.com"
  }
}
```

Errors:

| Status | Body |
|---|---|
| 400 | Validation error |
| 401 | `{ "detail": "User exists. Try logging in." }` |

#### Login

```
POST /api/auth/login
Content-Type: application/json
```

Request:

```json
{
  "email": "rahul@example.com",
  "password": "test1234"
}
```

Response `200` (sets `Access_Token` HTTP-only cookie):

```json
{
  "message": "Login successful",
  "user": {
    "id": "671abc...",
    "name": "Rahul",
    "email": "rahul@example.com"
  }
}
```

Errors:

| Status | Body |
|---|---|
| 401 | `{ "detail": "Invalid email or password" }` |

#### Current User

```
GET /api/auth/me
Cookie: Access_Token=<jwt>
```

Response `200`:

```json
{
  "user": {
    "id": "671abc...",
    "name": "Rahul",
    "email": "rahul@example.com"
  }
}
```

#### Logout

```
POST /api/auth/logout
```

Clears the `Access_Token` cookie.

### Documents

#### Upload

```
POST /api/documents/upload
Content-Type: multipart/form-data
Cookie: Access_Token=<jwt>
```

Form field:

| Field | Type | Description |
|---|---|---|
| `file` | File | PDF, DOCX, or TXT |

Response `201`:

```json
{
  "message": "File uploaded",
  "document": {
    "id": "671abc...",
    "filename": "policy.pdf",
    "size": 245000,
    "source_type": "pdf",
    "status": "pending",
    "uploaded_at": "2026-09-19T10:23:45"
  }
}
```

Ingestion runs in the background. The document status progresses from `pending` → `processing` → `ready` (or `failed`).

Errors:

| Status | Body |
|---|---|
| 400 | Unsupported file type |
| 401 | Not authenticated |
| 422 | Missing file field |

#### List Documents

```
GET /api/documents
Cookie: Access_Token=<jwt>
```

Response `200`:

```json
[
  {
    "id": "671abc...",
    "filename": "policy.pdf",
    "size": 245000,
    "source_type": "pdf",
    "status": "ready",
    "uploaded_at": "2026-09-19T10:23:45"
  }
]
```

#### Get Document

```
GET /api/documents/{document_id}
Cookie: Access_Token=<jwt>
```

Response `200`: same shape as one element of the list above.

Errors:

| Status | Body |
|---|---|
| 401 | Not authenticated |
| 404 | Document not found or not owned by the user |

### Query

```
POST /api/query
Content-Type: application/json
Cookie: Access_Token=<jwt>
```

Request:

```json
{
  "question": "What is the economic impact of AI for India?"
}
```

Response `200`:

```json
{
  "answer": "AI is estimated by Accenture to boost India's annual growth rate by 1.3 percentage points by 2035.",
  "sources": [
    {
      "chunk_number": 1,
      "document_id": "671abc...",
      "text": "Accenture... estimates AI to boost India's annual growth rate by 1.3 percentage points by 2035."
    }
  ]
}
```

Errors:

| Status | Body |
|---|---|
| 401 | Not authenticated |
| 422 | Invalid question |
| 502 | LLM returned invalid JSON |

---

## Data Models

### User

Collection: `users`

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | Primary key |
| `name` | String | 3–15 characters |
| `email` | String | Unique, validated |
| `password_hash` | String | bcrypt hash |
| `role` | String | `user` or `admin` |
| `created_at` | DateTime | Auto-set |

### UploadedDocument

Collection: `documents`

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | Primary key |
| `filename` | String | Original filename |
| `stored_path` | String | Path on disk |
| `size` | Integer | Bytes |
| `source_type` | String | `pdf`, `docx`, `txt` |
| `status` | String | `pending`, `processing`, `ready`, `failed` |
| `uploaded_by` | String | User ID |
| `uploaded_at` | DateTime | Auto-set |

### Chunk

Collection: `chunks` (reserved for future persistence)

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | Primary key |
| `document_id` | ObjectId | Parent document |
| `chunk_index` | Integer | Position within document |
| `text` | String | Chunk content |
| `embedding` | List[Float] | 1536-dim vector |
| `page_number` | Integer | Optional |
| `section_heading` | String | Optional |

### Pinecone Vector

Each chunk is stored as a vector with the following structure:

```
id:       "<document_id>#chunk<n>"
values:   [float, ...] (1536)
metadata: {
    document_id: "<id>",
    chunk_index: <n>,
    text: "<chunk text>"
}
```

---

## RAG Pipeline

### Ingestion (offline, per document)

1. **Parse** — `pypdf` extracts raw text from the PDF.
2. **Chunk** — `RecursiveCharacterTextSplitter` splits into 500-character pieces with 100-character overlap.
3. **Embed** — Gemini `gemini-embedding-2` embeds each chunk in batches of 50, with 2-second delays between batches to respect free-tier rate limits.
4. **Store** — Pinecone upserts each vector with its metadata. Document status is set to `ready`.

Ingestion handles:

- Gemini's 100-request batch limit (batching).
- Gemini's 100-request-per-minute rate limit (pacing).
- Transient 429 and 503 errors (retry with exponential backoff, 60-second waits on 429).
- Partial failures (document is marked `failed`, partial vectors cleared on retry).

### Retrieval and Generation (online, per query)

1. **Embed the question** using the same Gemini model.
2. **Query Pinecone** for the top-K nearest chunks by cosine similarity.
3. **Build the prompt** — question plus retrieved chunks, numbered for citation.
4. **Call Gemini** `gemini-3.6-flash` with a strict prompt: answer only from context, return JSON in a fixed shape.
5. **Validate** the LLM output against the `LLMAnswer` Pydantic schema.
6. **Return** the answer and the source chunks that were passed to the model.

If retrieval returns zero chunks, the endpoint responds with `"I don't know based on the provided documents."` rather than calling the LLM.

---

## Testing

The project includes a test suite that verifies the HTTP layer — authentication, validation, upload, and query endpoints. It does not test the RAG quality; that is handled by the evaluation suite.

### Running tests

```bash
pytest -v
```

Expected output:

```
tests/test_auth.py::test_register_then_login PASSED                    [  7%]
tests/test_documents.py::test_upload_requires_auth PASSED              [ 15%]
tests/test_documents.py::test_upload_rejects_unsupported_extension PASSED [ 23%]
tests/test_documents.py::test_upload_accepts_pdf PASSED                [ 30%]
tests/test_documents.py::test_list_documents_requires_auth PASSED      [ 38%]
tests/test_documents.py::test_list_documents_empty_for_new_user PASSED [ 46%]
tests/test_documents.py::test_list_documents_after_upload PASSED       [ 53%]
tests/test_documents.py::test_get_document_by_id PASSED                [ 61%]
tests/test_documents.py::test_get_nonexistent_document_returns_404 PASSED [ 69%]
tests/test_query.py::test_query_requires_auth PASSED                   [ 76%]
tests/test_query.py::test_query_rejects_empty_question PASSED          [ 84%]
tests/test_query.py::test_query_returns_answer_with_mocked_llm PASSED  [ 92%]
tests/test_query.py::test_query_returns_graceful_message_when_no_chunks PASSED [100%]

13 passed in 74.79s
```

### What is covered

| Category | Tests |
|---|---|
| Authentication enforcement | Three tests verify 401 on protected routes without a cookie |
| Input validation | Duplicate email, wrong password, bad extension, empty question |
| Happy path | Register, login, upload, list, get by ID, query |
| Not-found handling | Missing document returns 404, not 401 |
| Graceful degradation | Query with no chunks returns a friendly message, not a crash |

### What is not covered

- Retrieval quality (see Evaluation).
- Real Gemini API calls (mocked in `test_query.py`).
- Real PDF ingestion (mocked with `patch`).
- Performance and concurrency.

---

## Evaluation

Retrieval quality is measured separately with an offline evaluation suite.

### Golden set

`eval/datasets/qa.jsonl` contains 30 questions with expected keywords, drawn from two corpora:

- The NITI Aayog *National Strategy for Artificial Intelligence* (2018).
- A peer-reviewed clinical article on the nervous system.

### Metric

`recall@K` — for each question, does any of the top-K retrieved chunks contain all expected keywords?

```
recall@K = hits / total_questions
```

### Running the evaluation

```bash
python -m eval.runner 5
```

Sample output:

```
Evaluating 30 questions at top_k=5

  [01] HIT   What is the Accenture estimate of AI's contribution to India
  [02] MISS  How much is AI expected to add to India's economy by 2035?
  [03] HIT   Which organisation was mandated to establish the National Progra
  [04] HIT   What does the #AIforAll brand signify for India?
  [05] HIT   What are the five focus sectors identified by NITI Aayog for AI
  ...

Recall@5: 0.83  (25/30)
```

### Interpreting the number

| Recall@5 | Interpretation |
|---|---|
| ≥ 0.85 | Strong. Ready for generation tuning. |
| 0.60 – 0.85 | Acceptable. Investigate misses; consider larger top-K. |
| < 0.60 | Retrieval is weak. Re-examine chunk size, embedding model, or corpus. |

### Known misses and their causes

- **Figure captions not extracted.** Questions whose answers live inside PDF figures score MISS because the parser does not extract caption text. This is a corpus gap, not a retrieval bug.
- **Very specific terminology.** Questions using rare terms (e.g., `satellite glia`) occasionally miss because their embeddings score low against the general corpus.

These are the kinds of cases the eval is designed to surface.

---

## Known Limitations

1. **Ingestion runs in-process.** `BackgroundTasks` does not survive server restarts. Production systems use a queue (Celery, Arq, SQS).
2. **Uploaded files are stored on local disk.** Multi-server deployments require object storage (S3, GCS, or MongoDB GridFS).
3. **No embedding cache.** Re-running evaluation re-embeds every question. A cache keyed by content hash would eliminate this cost.
4. **Free-tier Gemini quota.** Ingestion and evaluation are rate-limited. Production requires a paid tier or a self-hosted embedding model.
5. **No answer faithfulness evaluation.** The current eval measures retrieval only. Faithfulness requires an LLM-as-judge step.
6. **`utcnow` deprecation.** The code uses `datetime.utcnow()`, which is deprecated in Python 3.12. Migration to `datetime.now(timezone.utc)` is pending.
7. **No structured logging.** The code uses `print()`. Production requires `logging` or `structlog` with JSON output.

---

## Roadmap

Planned improvements, in order of impact:

1. **Embedding cache** — avoid re-embedding identical questions; makes evaluation instantaneous.
2. **Structured logging** — replace `print()` with JSON logs and log levels.
3. **Answer faithfulness evaluation** — add LLM-as-judge metrics: faithfulness, answer relevance, citation accuracy.
4. **Real background queue** — replace `BackgroundTasks` with Arq and Redis.
5. **Object storage** — move uploads to S3 or GridFS.
6. **Docker** — add a `Dockerfile` and `docker-compose.yml` for reproducible deployment.
7. **CI integration** — run tests and evaluation on every pull request.

---

## License

This project is provided as-is for educational and portfolio purposes.

---

## Acknowledgements

Built with FastAPI, Beanie, Pinecone, and Google Gemini. Evaluation methodology informed by standard practice in production RAG systems: golden datasets, recall@K, and error-driven iteration.