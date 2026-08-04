"""RAG backend for PawPal+ AI Dog Care Guide."""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from pathlib import Path
from typing import Callable, Optional

LOGGER = logging.getLogger("pawpal.ai")
if not LOGGER.handlers:
    logging.basicConfig(
        filename=os.getenv("PAWPAL_LOG_FILE", "pawpal_ai.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

KNOWLEDGE_PATH = Path(__file__).with_name("knowledge_base.json")
EMERGENCY_TERMS = (
    "cannot breathe", "can't breathe", "difficulty breathing", "not breathing",
    "seizure", "unconscious", "severe bleeding", "collapsed", "collapse",
    "ate xylitol", "eaten xylitol", "poisoned", "overdose",
)
MEDICATION_TERMS = ("dose", "dosage", "double the", "prescribe", "medication", "medicine", "drug")
NON_DOG_TERMS = ("cat", "kitten", "iguana", "bird", "rabbit", "hamster", "horse", "ferret")
STOP_WORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "is",
    "it", "my", "of", "often", "should", "the", "to", "what", "with",
}


def load_knowledge_base(path: Path = KNOWLEDGE_PATH) -> list[dict]:
    """Load and minimally validate the local knowledge records."""
    with path.open(encoding="utf-8") as file:
        records = json.load(file)
    required = {"id", "topic", "keywords", "content", "source", "source_url"}
    if not isinstance(records, list) or any(not required.issubset(record) for record in records):
        raise ValueError("knowledge_base.json has an invalid structure")
    return records


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    normalized = set()
    for word in words:
        if word in STOP_WORDS:
            continue
        normalized.add(word)
        if word.endswith("ing") and len(word) > 5:
            normalized.add(word[:-3])
        elif word.endswith("s") and len(word) > 3:
            normalized.add(word[:-1])
    return normalized


def retrieve_context(question: str, records: Optional[list[dict]] = None, limit: int = 2) -> list[dict]:
    """Return records ranked by transparent keyword overlap."""
    records = records if records is not None else load_knowledge_base()
    query_tokens = _tokens(question)
    ranked = []
    for record in records:
        keyword_tokens = _tokens(" ".join(record["keywords"]))
        document_tokens = _tokens(f'{record["topic"]} {record["content"]}')
        score = 3 * len(query_tokens & keyword_tokens) + len(query_tokens & document_tokens)
        if score > 0:
            ranked.append((score, record["id"], record))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [dict(item[2], retrieval_score=item[0]) for item in ranked[:limit]]


def check_guardrail(question: str) -> Optional[dict]:
    """Return a safe response when deterministic input rules match."""
    normalized = " ".join(question.lower().split())
    contains = lambda term: re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", normalized) is not None
    if not normalized:
        return {"status": "error", "answer": "Please enter a dog-care question.", "sources": []}
    if any(contains(term) for term in NON_DOG_TERMS):
        return {
            "status": "unsupported_species",
            "answer": "PawPal+ currently supports dogs only. Please use a species-specific trusted resource or veterinarian for another animal.",
            "sources": [],
        }
    if any(contains(term) for term in EMERGENCY_TERMS):
        return {
            "status": "emergency",
            "answer": "This may be an emergency. Contact an emergency veterinarian immediately. PawPal+ cannot diagnose or replace veterinary care.",
            "sources": [],
        }
    if any(contains(term) for term in MEDICATION_TERMS):
        return {
            "status": "medication_safety",
            "answer": "PawPal+ cannot choose, calculate, or change medication dosage. Follow the prescribing veterinarian's instructions or contact the clinic.",
            "sources": [],
        }
    return None


def build_prompt(question: str, dog_profile: dict, contexts: list[dict]) -> str:
    """Build the grounded user prompt sent to the model."""
    profile = ", ".join(f"{key}: {value}" for key, value in dog_profile.items() if value) or "No profile provided"
    evidence = "\n\n".join(
        f'[{index}] {item["topic"]}: {item["content"]}' for index, item in enumerate(contexts, start=1)
    )
    return f"""Dog profile: {profile}

Question: {question}

Retrieved evidence:
{evidence}

Answer in 2-5 sentences using only the retrieved evidence for factual care claims.
Use the profile only to make the response more relevant; do not infer a diagnosis.
If the evidence cannot answer the question, say the local knowledge base is insufficient.
Do not prescribe medication, calculate food portions, or replace veterinary advice.
Refer to evidence using [1] or [2]."""


def _call_openai_http(prompt: str) -> str:
    """Attempt to call OpenAI via the HTTP API if the SDK is unavailable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "The OPENAI_API_KEY environment variable is not set. Export it before running the app."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    url = "https://api.openai.com/v1/responses"
    request_data = json.dumps({
        "model": model,
        "instructions": (
            "You are PawPal+, a cautious dog-care education assistant. "
            "Follow the supplied evidence and safety constraints exactly."
        ),
        "input": prompt,
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except Exception as error:
        raise RuntimeError(
            "OpenAI HTTP API request failed. Check network access, the API key, and whether the OpenAI endpoint is reachable."
        ) from error

    try:
        data = json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError("OpenAI response could not be decoded as JSON") from error

    if "output" in data and isinstance(data["output"], dict):
        if "text" in data["output"]:
            return data["output"]["text"].strip()
        if "content" in data["output"] and isinstance(data["output"]["content"], list):
            for item in data["output"]["content"]:
                if isinstance(item, dict) and item.get("type") == "output_text":
                    return item.get("text", "").strip()
    raise RuntimeError("OpenAI response did not contain expected output fields")


def call_openai(prompt: str) -> str:
    """Generate an answer with OpenAI. Prefer the SDK, fall back to HTTP if needed."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "The OPENAI_API_KEY environment variable is not set. Export it before running the app."
        )

    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            instructions=(
                "You are PawPal+, a cautious dog-care education assistant. "
                "Follow the supplied evidence and safety constraints exactly."
            ),
            input=prompt,
        )
        if hasattr(response, "output_text"):
            return response.output_text.strip()
        if hasattr(response, "output") and isinstance(response.output, dict):
            return response.output.get("text", "").strip()
        raise RuntimeError("OpenAI SDK response missing expected text output")
    except ImportError:
        return _call_openai_http(prompt)
    except Exception as error:
        raise RuntimeError("OpenAI SDK request failed") from error


def answer_question(
    question: str,
    dog_profile: Optional[dict] = None,
    generator: Optional[Callable[[str], str]] = None,
) -> dict:
    """Run guardrails, retrieval, grounded generation, and source collection."""
    guardrail = check_guardrail(question)
    if guardrail:
        LOGGER.warning("guardrail status=%s", guardrail["status"])
        return guardrail

    contexts = retrieve_context(question)
    if not contexts:
        LOGGER.info("insufficient_context")
        return {
            "status": "insufficient_context",
            "answer": "I don't have enough relevant information in the local dog-care knowledge base to answer that safely.",
            "sources": [],
        }

    prompt = build_prompt(question, dog_profile or {}, contexts)
    try:
        answer = (generator or call_openai)(prompt)
        if not answer:
            raise ValueError("The model returned an empty response")
    except Exception as error:
        LOGGER.exception("generation_failed error_type=%s", type(error).__name__)
        return {
            "status": "generation_error",
            "answer": "I found relevant information, but the AI response could not be generated. Check the API key and try again.",
            "sources": [],
        }

    sources = [
        {"title": item["source"], "url": item["source_url"], "document_id": item["id"]}
        for item in contexts
    ]
    LOGGER.info("answer_generated documents=%s", [item["id"] for item in contexts])
    return {"status": "ok", "answer": answer, "sources": sources}
