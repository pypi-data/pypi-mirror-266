"""Dataclasses for embeddings."""

from typing import List

from pydantic import BaseModel


class EmbeddingMeta(BaseModel):
    """Metadata for an embedding output."""

    text: str
    embedding: List[float]
