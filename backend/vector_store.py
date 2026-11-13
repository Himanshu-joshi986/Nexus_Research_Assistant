import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DIR, EMBEDDING_MODEL

_client = None
_model = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _collection(name: str):
    return _get_client().get_or_create_collection(name)


def store_chunks(session_id: str, chunks: list[str], metadatas: list[dict]):
    col = _collection(f"session_{session_id}")
    model = _get_model()
    embeddings = model.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    col.add(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)
    return len(chunks)


def retrieve_relevant(session_id: str, query: str, n_results: int = 5) -> list[dict]:
    col = _collection(f"session_{session_id}")
    model = _get_model()
    q_emb = model.encode([query]).tolist()
    try:
        results = col.query(query_embeddings=q_emb, n_results=n_results, include=["documents", "metadatas", "distances"])
        items = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            items.append({"text": doc, "meta": meta, "score": round(1 - dist, 4)})
        return items
    except Exception:
        return []


def delete_session(session_id: str):
    try:
        _get_client().delete_collection(f"session_{session_id}")
    except Exception:
        pass

