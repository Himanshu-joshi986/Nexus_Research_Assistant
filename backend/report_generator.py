import asyncio
import httpx
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    HUGGINGFACE_API_KEY, HUGGINGFACE_BASE_URL, HUGGINGFACE_MODEL,
)


def _messages(prompt: str, system: str = "") -> list[dict]:
    msgs = [{"role": "system", "content": system}] if system else []
    return msgs + [{"role": "user", "content": prompt}]


async def _post_chat(url: str, headers: dict, model: str, messages: list[dict]) -> httpx.Response:
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        return await client.post(
            url,
            headers={**headers, "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": 3000},
        )


async def _call_openrouter(prompt: str, system: str = "") -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AI Research Assistant",
    }
    messages = _messages(prompt, system)
    for _ in range(3):
        resp = await _post_chat(f"{OPENROUTER_BASE_URL}/chat/completions", headers, OPENROUTER_MODEL, messages)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "30")
            await asyncio.sleep((int(retry_after) if retry_after.isdigit() else 30) + 2)
            continue
        if not resp.is_success:
            raise Exception(f"OpenRouter {resp.status_code}: {resp.text}")
        result = resp.json()
        print(f"[OpenRouter OK] model={result.get('model')} tokens={result.get('usage')}")
        return result["choices"][0]["message"]["content"]
    raise Exception("OpenRouter rate limit exceeded after retries.")


async def _call_huggingface(prompt: str, system: str = "") -> str:
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    resp = await _post_chat(f"{HUGGINGFACE_BASE_URL}/chat/completions", headers, HUGGINGFACE_MODEL, _messages(prompt, system))
    if not resp.is_success:
        raise Exception(f"HuggingFace {resp.status_code}: {resp.text}")
    print("[HuggingFace OK] used as backup")
    return resp.json()["choices"][0]["message"]["content"]


async def _call_llm(prompt: str, system: str = "") -> str:
    try:
        return await _call_openrouter(prompt, system)
    except Exception as err:
        print(f"[OpenRouter failed] {err}")
        or_err = err
    if not HUGGINGFACE_API_KEY:
        raise Exception(f"OpenRouter failed: {or_err}")
    try:
        return await _call_huggingface(prompt, system)
    except Exception as hf_err:
        print(f"[HuggingFace failed] {hf_err}")
        raise Exception(f"OpenRouter failed: {or_err} | HuggingFace backup failed: {hf_err}")


async def generate_report(topic: str, depth: str, chunks: list[dict], entities: list, keywords: list) -> str:
    context = "\n\n".join(f"[Source: {c['meta'].get('url', '')}]\n{c['text']}" for c in chunks[:15])
    kw_str = ", ".join(k["word"] for k in keywords[:10])
    ent_str = ", ".join(dict.fromkeys(e["text"] for e in entities[:15]))

    system = (
        "You are an expert research analyst. Write a comprehensive, well-structured research report "
        "using only the provided context. Use markdown formatting with headers, bullet points, and sections."
    )
    prompt = f"""Write a {depth}-level research report on: **{topic}**

Key Entities: {ent_str}
Key Concepts: {kw_str}

Context from sources:
{context}

Structure the report with:
1. Executive Summary
2. Introduction
3. Key Findings (with subsections)
4. Analysis
5. Conclusion
6. References (list the source URLs used)

Write in an academic yet readable style."""

    return await _call_llm(prompt, system)


async def chat_with_report(report_content: str, question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(c["text"] for c in chunks[:5])
    prompt = f"""Based on this research report and supporting context, answer the question.

Report Summary:
{report_content[:2000]}

Additional Context:
{context}

Question: {question}

Provide a clear, concise answer based only on the information above."""
    return await _call_llm(prompt)
