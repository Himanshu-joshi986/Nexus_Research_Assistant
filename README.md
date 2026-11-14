# AI Research Assistant

An AI-powered research application that searches the web, extracts and analyzes source material, and generates research reports. The project includes a FastAPI backend and a responsive browser-based frontend.

## Contents

- [Features](#features)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Getting started](#getting-started)
- [API](#api)
- [Project structure](#project-structure)
- [Configuration](#configuration)
- [Data files](#data-files)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)

## Features

- Search the web with Tavily and extract article text with Trafilatura.
- Analyze content with NLTK, spaCy, and KeyBERT.
- Create embeddings and store them in ChromaDB for retrieval-augmented generation (RAG).
- Generate structured Markdown reports and answer questions about them with an OpenRouter model.
- Sign in with a locally configured account and browse saved research history.
- Review report sources, keyword scores, and color-coded named entities.
- View research statistics, including report counts, depth distribution, and keyword trends.
- Use the responsive frontend on desktop or mobile.

## How it works

1. Enter a topic and choose research depth and recency.
2. Tavily finds relevant pages, and Trafilatura extracts their text.
3. The NLP pipeline identifies entities and keywords and prepares the text.
4. Sentence Transformers creates embeddings, which are stored in ChromaDB.
5. Relevant passages are retrieved and sent to the configured OpenRouter model to draft a report.
6. The report is saved and shown in the frontend.

## Requirements

- Python 3.11.9 (the repository's `.python-version`)
- A [Tavily API key](https://tavily.com/)
- An [OpenRouter API key](https://openrouter.ai/)

## Getting started

### 1. Configure the backend

Copy `backend/.env.example` to `backend/.env`, then add your API keys and choose a private admin password:

```env
TAVILY_API_KEY=your-tavily-key
OPENROUTER_API_KEY=your-openrouter-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=choose-a-private-password
ADMIN_NAME=Admin User
```

Keep `.env` files and API keys private. They are ignored by Git.

### 2. Install dependencies

From the project root, run the setup script in Windows Command Prompt or PowerShell:

```bat
setup.bat
```

The script creates a virtual environment, installs Python dependencies, downloads the spaCy model, and prepares NLTK data.

### 3. Start the backend

```bat
start.bat
```

The API will be available at `http://localhost:8000`. The interactive API documentation is at `http://localhost:8000/docs`.

### 4. Open the frontend

Open `frontend/index.html` in your browser. By default, the frontend connects to the backend at `http://localhost:8000`.

On first launch, the backend creates an admin account from the `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `ADMIN_NAME` settings if `backend/data/users.json` does not exist. If `backend/data/reports.json` is missing, it uses the sample data in `backend/data/demo_reports.json`.

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/login` | Authenticate a user |
| `POST` | `/api/research/stream` | Start research and stream progress using SSE |
| `GET` | `/api/reports` | List reports |
| `GET` | `/api/reports/{id}` | Get a report |
| `DELETE` | `/api/reports/{id}` | Delete a report |
| `POST` | `/api/chat` | Ask questions about a report using RAG |
| `GET` | `/api/stats` | Get research statistics |
| `GET` | `/health` | Check backend health |

## Project structure

```text
Research_model/
├── backend/
│   ├── data/                  # Runtime user, report, and vector-store data
│   ├── main.py                # FastAPI application and endpoints
│   ├── config.py              # Application and model configuration
│   ├── storage.py             # JSON file operations
│   ├── nlp_processor.py       # NLTK, spaCy, and KeyBERT pipeline
│   ├── vector_store.py        # ChromaDB and Sentence Transformers
│   ├── searcher.py            # Tavily search and Trafilatura extraction
│   ├── report_generator.py    # OpenRouter report generation
│   ├── requirements.txt
│   └── .env.example           # Environment variable template
├── frontend/
│   ├── index.html             # Login page
│   ├── pages/                 # Dashboard, research, report, and history views
│   ├── components/            # Shared JavaScript, API config, and sidebar
│   └── styles/                # Responsive CSS
├── setup.bat                  # Install dependencies and NLP data
├── start.bat                  # Start the local backend
├── DEPLOYMENT.md              # GitHub Pages and Render instructions
└── README.md
```

## Configuration

Edit `backend/config.py` to adjust the application defaults:

| Setting | Purpose | Current default |
| --- | --- | --- |
| `OPENROUTER_MODEL` | Report generation model | `meta-llama/llama-3.1-8b-instruct` |
| `DEPTH_CONFIG` | Search results / retrieved chunks | Basic: 5 / 10; Medium: 10 / 20; Advanced: 15 / 30 |
| `RECENCY_DAYS` | Date range for each recency option | 1 Month: 30; 6 Months: 180; 1 Year: 365 days |
| `EMBEDDING_MODEL` | Sentence Transformers embedding model | `all-MiniLM-L6-v2` |

## Data files

The backend stores local accounts and reports as JSON files and creates a persistent ChromaDB vector store under `backend/data/` as needed. Runtime data is local and should not be committed. The account file contains the configured password, so use a private password and keep this file out of source control.

The account file has this shape:

```json
{
  "users": [
    {
      "id": "u1",
      "username": "admin",
      "password": "<value from ADMIN_PASSWORD>",
      "name": "Admin User",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

A report record has this shape:

```json
{
  "reports": [
    {
      "id": "uuid",
      "user_id": "u1",
      "username": "admin",
      "topic": "Quantum Computing",
      "depth": "Medium",
      "recency": "6 Months",
      "report": "## Executive Summary...",
      "keywords": [{"word": "quantum", "score": 0.85}],
      "entities": [{"text": "IBM", "label": "ORG"}],
      "sources": [{"url": "https://example.com", "title": "Example source"}],
      "session_id": "uuid",
      "word_count": 1200,
      "created_at": "2024-01-01T12:00:00"
    }
  ]
}
```

The tracked `demo_reports.json` file provides sample reports when no local report file exists.

## Troubleshooting

**spaCy model not found**

```bash
python -m spacy download en_core_web_sm
```

**CORS errors**

Make sure the backend is running on port `8000` before opening the frontend.

**First research run is slow**

Sentence Transformers downloads its embedding model on first use. Later runs can reuse the downloaded model.

**API key errors**

Check that both keys are set in `backend/.env` and that there are no spaces around the `=` signs.

**Frontend cannot reach the deployed backend**

The frontend API URL is set in `frontend/components/config.js` and defaults to `http://localhost:8000`. For a deployed site, update it to the backend URL as described in [DEPLOYMENT.md](./DEPLOYMENT.md).

## Deployment

For GitHub Pages and Render deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

