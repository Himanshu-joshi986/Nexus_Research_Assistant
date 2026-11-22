import asyncio
import json
import traceback
import uuid
from collections import Counter
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import storage
import nlp_processor
import vector_store
import searcher
import report_generator
from config import DEPTH_CONFIG

app = FastAPI(title="AI Research Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Models ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class ResearchRequest(BaseModel):
    user_id: str
    username: str
    topic: str
    depth: str = "Medium"
    recency: str = "6 Months"


class ChatRequest(BaseModel):
    report_id: str
    session_id: str
    question: str


# ---------- Auth ----------
@app.post("/api/login")
def login(req: LoginRequest):
    user = storage.get_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "user": {"id": user["id"], "username": user["username"], "name": user["name"]}}


# ---------- Research (SSE Streaming) ----------
async def research_pipeline(req: ResearchRequest) -> AsyncGenerator[str, None]:
    session_id = str(uuid.uuid4())

    def emit(step: int, message: str, data: dict = None):
        payload = {"step": step, "message": message, "session_id": session_id}
        if data:
            payload.update(data)
        return f"data: {json.dumps(payload)}\n\n"

    try:
        yield emit(1, "Searching the web for relevant content...")
        await asyncio.sleep(0.1)
        results = await asyncio.to_thread(searcher.search_web, req.topic, req.depth, req.recency)
        if not results:
            yield emit(0, "No search results found.", {"error": True})
            return

        yield emit(2, f"Found {len(results)} sources. Scraping content...")
        await asyncio.sleep(0.1)
        articles = await asyncio.to_thread(searcher.scrape_all, results)
        if not articles:
            yield emit(0, "Could not scrape any content.", {"error": True})
            return

        yield emit(3, f"Scraped {len(articles)} articles. Running NLP preprocessing...")
        await asyncio.sleep(0.1)

        all_entities, all_keywords, all_chunks, chunk_metas = [], [], [], []
        for article in articles:
            nlp_result = await asyncio.to_thread(nlp_processor.preprocess, article["text"])
            all_entities.extend(nlp_result["entities"])
            all_keywords.extend(nlp_result["keywords"])
            chunks = nlp_processor.chunk_text(article["text"])
            all_chunks.extend(chunks)
            chunk_metas.extend({"url": article["url"], "title": article["title"]} for _ in chunks)

        # Deduplicate keywords by word, keeping the highest score for each
        best = {}
        for k in sorted(all_keywords, key=lambda x: -x["score"]):
            best.setdefault(k["word"], k)
        unique_keywords = list(best.values())

        yield emit(4, f"Processed {len(all_chunks)} chunks. Generating embeddings...")
        await asyncio.sleep(0.1)
        max_chunks = DEPTH_CONFIG[req.depth]["max_chunks"]
        store_chunks = all_chunks[:max_chunks]
        store_metas = chunk_metas[:max_chunks]
        await asyncio.to_thread(vector_store.store_chunks, session_id, store_chunks, store_metas)

        yield emit(5, "Retrieving relevant chunks with RAG...")
        await asyncio.sleep(0.1)
        relevant = await asyncio.to_thread(vector_store.retrieve_relevant, session_id, req.topic, n_results=10)

        yield emit(6, "Generating research report with AI...")
        await asyncio.sleep(0.1)
        report_text = await report_generator.generate_report(
            req.topic, req.depth, relevant, all_entities, unique_keywords
        )

        yield emit(7, "Saving report...")
        sources = [{"url": a["url"], "title": a["title"]} for a in articles]
        report = {
            "user_id": req.user_id,
            "username": req.username,
            "topic": req.topic,
            "depth": req.depth,
            "recency": req.recency,
            "report": report_text,
            "keywords": unique_keywords[:20],
            "entities": all_entities[:30],
            "sources": sources,
            "session_id": session_id,
            "word_count": len(report_text.split()),
        }
        report_id = await asyncio.to_thread(storage.save_report, report)

        yield emit(8, "Research complete!", {
            "done": True,
            "report_id": report_id,
            "report": report_text,
            "keywords": unique_keywords[:20],
            "entities": all_entities[:30],
            "sources": sources,
        })

    except Exception as e:
        traceback.print_exc()
        yield emit(0, f"Error: {str(e)}", {"error": True})


@app.post("/api/research/stream")
async def research_stream(req: ResearchRequest):
    return StreamingResponse(
        research_pipeline(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- Reports ----------
@app.get("/api/reports")
def list_reports(user_id: str = None):
    return storage.get_reports(user_id)


@app.get("/api/reports/{report_id}")
def get_report(report_id: str):
    r = storage.get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return r


@app.delete("/api/reports/{report_id}")
def delete_report(report_id: str):
    removed = storage.delete_report(report_id)
    if removed and removed.get("session_id"):
        vector_store.delete_session(removed["session_id"])
    return {"success": True}


# ---------- Chat with Report ----------
@app.post("/api/chat")
async def chat(req: ChatRequest):
    report = storage.get_report(req.report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    relevant = await asyncio.to_thread(
        vector_store.retrieve_relevant, req.session_id, req.question, n_results=5
    )
    answer = await report_generator.chat_with_report(
        report["report"], req.question, relevant
    )
    return {"answer": answer}


# ---------- Stats ----------
@app.get("/api/stats")
def get_stats(user_id: str = None):
    reports = storage.get_reports(user_id)
    depths = Counter(r.get("depth", "Medium") for r in reports)
    kw_freq = Counter(k["word"] for r in reports for k in r.get("keywords", []))
    return {
        "total_reports": len(reports),
        "topics": [r["topic"] for r in reports],
        "depth_distribution": dict(depths),
        "top_keywords": [{"word": w, "count": c} for w, c in kw_freq.most_common(30)],
    }
