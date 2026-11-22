import uuid
from functools import cache

import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DIR, EMBEDDING_MODEL


@cache
def _get_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


@cache
def _get_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def _collection(session_id: str):
    return _get_client().get_or_create_collection(f"session_{session_id}")


def store_chunks(session_id: str, chunks: list[str], metadatas: list[dict]):
    embeddings = _get_model().encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    _collection(session_id).add(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)
    return len(chunks)


def retrieve_relevant(session_id: str, query: str, n_results: int = 5) -> list[dict]:
    q_emb = _get_model().encode([query]).tolist()
    try:
        results = _collection(session_id).query(
            query_embeddings=q_emb, n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []
    return [
        {"text": doc, "meta": meta, "score": round(1 - dist, 4)}
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ]


def delete_session(session_id: str):
    try:
        _get_client().delete_collection(f"session_{session_id}")
    except Exception:
        pass
