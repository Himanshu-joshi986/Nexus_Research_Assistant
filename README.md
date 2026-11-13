# ðŸ§  AI Research Assistant

A complete AI-powered research assistant built for a final-year college project. It searches the web, scrapes content, processes it with NLP, stores it in a vector database, and generates detailed research reports using an LLM.

## ðŸ“ Project Structure

```
Research_model/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ data/
â”‚   â”‚   â”œâ”€â”€ users.json          # Local user credentials (ignored by Git)
â”‚   â”‚   â”œâ”€â”€ reports.json        # Saved research reports (ignored by Git)
â”‚   â”‚   â””â”€â”€ chroma_db/          # ChromaDB vector store (auto-created)
â”‚   â”œâ”€â”€ main.py                 # FastAPI app + all endpoints
â”‚   â”œâ”€â”€ config.py               # Configuration and constants
â”‚   â”œâ”€â”€ storage.py              # JSON file operations
â”‚   â”œâ”€â”€ nlp_processor.py        # NLTK, spaCy, KeyBERT pipeline
â”‚   â”œâ”€â”€ vector_store.py         # ChromaDB + SentenceTransformers
â”‚   â”œâ”€â”€ searcher.py             # Tavily search + Trafilatura scraping
â”‚   â”œâ”€â”€ report_generator.py     # OpenRouter LLM integration
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ .env                    # Local API keys (never commit)
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ index.html              # Login page
â”‚   â”œâ”€â”€ pages/
â”‚   â”‚   â”œâ”€â”€ dashboard.html      # Stats & overview
â”‚   â”‚   â”œâ”€â”€ research.html       # New research + progress tracker
â”‚   â”‚   â”œâ”€â”€ report.html         # Full report viewer + chat
â”‚   â”‚   â””â”€â”€ history.html        # Research history
â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â””â”€â”€ app.js              # Shared JS: auth, API, helpers
â”‚   â””â”€â”€ styles/
â”‚       â””â”€â”€ main.css            # Complete responsive CSS
â”œâ”€â”€ setup.bat                   # One-click setup
â”œâ”€â”€ start.bat                   # Start the server
â”œâ”€â”€ DEPLOYMENT.md               # GitHub Pages + Render setup
â””â”€â”€ README.md
```

## âš™ï¸ Prerequisites

- **Python 3.10+** installed and in PATH
- **Tavily API key** â†’ https://tavily.com (free tier available)
- **OpenRouter API key** â†’ https://openrouter.ai (model pricing and free availability vary)

## ðŸš€ Quick Start

### Step 1: Configure local environment
Copy `backend/.env.example` to `backend/.env` and set your API keys and a private local admin password. `.env` is ignored by Git:
```env
TAVILY_API_KEY=your-tavily-key
OPENROUTER_API_KEY=your-openrouter-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=choose-a-private-password
ADMIN_NAME=Admin User
```

### Step 2: Run Setup (first time only)
```bat
setup.bat
```
This installs all Python packages, the spaCy model, and NLTK data.

### Step 3: Start the Server
```bat
start.bat
```

### Step 4: Open the App
Open `frontend/index.html` directly in your browser.

If `backend/data/users.json` exists, the app uses those local accounts. If it is absent, the backend initializes the first admin account from the `ADMIN_USERNAME` and `ADMIN_PASSWORD` values in `backend/.env`. If `backend/data/reports.json` is missing, the app starts from `backend/data/demo_reports.json`.

For GitHub Pages + Render deployment, follow [DEPLOYMENT.md](./DEPLOYMENT.md). Never commit `.env` files or API keys. Local user/report files and ChromaDB data are also excluded from Git.

## ðŸ”Œ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Authenticate user |
| POST | `/api/research/stream` | Start research (SSE stream) |
| GET | `/api/reports` | List all reports |
| GET | `/api/reports/{id}` | Get single report |
| DELETE | `/api/reports/{id}` | Delete report |
| POST | `/api/chat` | Chat with a report (RAG) |
| GET | `/api/stats` | Research statistics |

**Interactive API docs:** http://localhost:8000/docs

## ðŸ”„ Research Workflow

```
User Input (topic + depth + recency)
        â†“
1. Tavily API â†’ Web Search Results
        â†“
2. Trafilatura â†’ Scrape Article Text
        â†“
3. NLTK â†’ Tokenize, Remove Stopwords, Lemmatize
   spaCy â†’ Named Entity Recognition
   KeyBERT â†’ Keyword Extraction
        â†“
4. Sentence Transformers â†’ Generate Embeddings
        â†“
5. ChromaDB â†’ Store Vectors
        â†“
6. ChromaDB â†’ RAG Retrieval (top-k chunks)
        â†“
7. OpenRouter (Mistral-7B) â†’ Generate Report
        â†“
8. reports.json â†’ Save Report
        â†“
Frontend â†’ Display Results
```

## ðŸ“Š Data Schemas

### users.json
```json
{
  "users": [{
    "id": "u1",
    "username": "admin",
    "password": "<local user password>",
    "name": "Admin User",
    "created_at": "2024-01-01T00:00:00"
  }]
}
```

### reports.json
```json
{
  "reports": [{
    "id": "uuid",
    "user_id": "u1",
    "username": "admin",
    "topic": "Quantum Computing",
    "depth": "Medium",
    "recency": "6 Months",
    "report": "## Executive Summary...",
    "keywords": [{"word": "quantum", "score": 0.85}],
    "entities": [{"text": "IBM", "label": "ORG"}],
    "sources": [{"url": "...", "title": "..."}],
    "session_id": "uuid",
    "word_count": 1200,
    "created_at": "2024-01-01T12:00:00"
  }]
}
```

## ðŸŽ›ï¸ Configuration

Edit `backend/config.py` to change:
- `OPENROUTER_MODEL` â€“ default: `mistralai/mistral-7b-instruct`
- `DEPTH_CONFIG` â€“ number of sources per depth level
- `RECENCY_DAYS` â€“ date range for each recency option
- `EMBEDDING_MODEL` â€“ default: `all-MiniLM-L6-v2`

## ðŸŒŸ Features

- **ðŸ” Login System** â€“ username/password auth with JSON storage
- **ðŸŒ Web Research** â€“ Tavily API searches with recency filtering
- **ðŸ“¥ Content Scraping** â€“ Trafilatura extracts clean article text
- **ðŸ§¬ NLP Pipeline** â€“ tokenization, stopwords, lemmatization, NER, keyword extraction
- **ðŸ”¢ Vector Embeddings** â€“ Sentence Transformers (all-MiniLM-L6-v2)
- **ðŸ—ƒï¸ Vector Storage** â€“ Persistent ChromaDB with semantic search
- **ðŸŽ¯ RAG** â€“ Retrieval Augmented Generation for accurate reports
- **âœï¸ AI Reports** â€“ Structured markdown reports via OpenRouter LLM
- **ðŸ’¬ Chat Interface** â€“ Ask questions about any report using RAG
- **â˜ï¸ Keyword Cloud** â€“ Visual keyword frequency display
- **ðŸ·ï¸ Named Entities** â€“ Color-coded entity type display
- **ðŸ”— Source Viewer** â€“ All scraped sources with links
- **ðŸ“Š Statistics** â€“ Report counts, depth distribution, keyword trends
- **ðŸ“š History** â€“ Searchable, filterable report archive
- **ðŸ“± Responsive** â€“ Works on desktop and mobile

## ðŸ› ï¸ Troubleshooting

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**CORS errors:** Ensure the backend is running on port 8000 before opening the frontend.

**Slow first run:** Sentence Transformer model downloads on first use (~90MB).

**API key errors:** Double-check `.env` file has no spaces around `=`.

