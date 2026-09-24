"""
Semantic experience memory, backed by ChromaDB.

This is what lets the agent find "a similar previous experience" even
when the new query is worded differently from the old one (e.g.
"weather in Mumbai" vs "what's it like in Mumbai right now").

Embeddings are produced by a small, fully offline hashing embedder
(see HashingEmbeddingFunction) -- no model download and no API key
required, so DEMO MODE never depends on the network.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Any

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings

from core.config import CONFIG
from core.models import Experience, SimilarExperience

EMBED_DIM = 256
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbeddingFunction(EmbeddingFunction):
    """
    Deterministic bag-of-words hashing embedder.

    Each token is hashed into one of EMBED_DIM buckets; the resulting
    vector is L2-normalized. Semantically close text (shared words,
    e.g. same tool + same city) lands close in cosine distance without
    needing any pretrained model or internet access.
    """

    def __call__(self, input: Documents) -> Embeddings:  # noqa: A002
        vectors: Embeddings = []
        for text in input:
            vec = [0.0] * EMBED_DIM
            for tok in _tokenize(text):
                h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
                vec[h % EMBED_DIM] += 1.0
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vectors.append([v / norm for v in vec])
        return vectors


_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        CONFIG.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CONFIG.chroma_persist_dir))
        _collection = _client.get_or_create_collection(
            name="tool_experiences",
            embedding_function=HashingEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_experience_embedding(exp: Experience) -> None:
    collection = _get_collection()
    collection.add(
        ids=[str(exp.id)],
        documents=[exp.query_text()],
        metadatas=[
            {
                "tool_name": exp.tool_name,
                "status": exp.status,
                "error_message": exp.error_message or "",
                "lessons_learned": exp.lessons_learned or "",
            }
        ],
    )


def query_similar(
    query_text: str, n_results: int = 3, min_similarity: float = 0.15
) -> list[SimilarExperience]:
    """
    Find previous experiences whose stored text is semantically close
    to `query_text`. Returns [] if the collection is empty (first run).
    """
    from core import database  # local import avoids a circular import

    collection = _get_collection()
    if collection.count() == 0:
        return []

    n_results = min(n_results, collection.count())
    results = collection.query(query_texts=[query_text], n_results=n_results)

    out: list[SimilarExperience] = []
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for exp_id, distance in zip(ids, distances):
        similarity = max(0.0, 1.0 - distance / 2.0)  # cosine distance -> 0..1
        if similarity < min_similarity:
            continue
        exp = database.get_experience_by_id(int(exp_id))
        if exp:
            out.append(SimilarExperience(experience=exp, similarity=similarity))
    return out


def collection_stats() -> dict[str, Any]:
    collection = _get_collection()
    return {"vector_count": collection.count()}
