"""Embedding utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


@dataclass(slots=True)
class EmbeddingConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "echograph_embeddings"
    vector_size: int | None = None


class EmbeddingService:
    """Generate and persist embeddings to Qdrant."""

    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        self.config = config or EmbeddingConfig()
        self.model = SentenceTransformer(self.config.model_name)
        self.client = QdrantClient(url=self.config.qdrant_url)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        dim = self.config.vector_size or self.model.get_sentence_embedding_dimension()
        self.client.recreate_collection(
            collection_name=self.config.collection_name,
            vectors_config={"size": dim, "distance": "Cosine"},
        )

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        vectors = self.model.encode(list(texts), show_progress_bar=False, convert_to_numpy=True)
        return vectors

    def upsert(self, texts: Sequence[str], metadata: Sequence[dict[str, str]]) -> None:
        vectors = self.embed(texts)
        payloads = list(metadata)
        ids = list(range(len(payloads)))
        self.client.upsert(
            collection_name=self.config.collection_name,
            points={"ids": ids, "payloads": payloads, "vectors": vectors.tolist()},
        )
