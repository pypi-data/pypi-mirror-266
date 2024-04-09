"""Dataclasses for embeddings."""

from typing import List
from pydantic import BaseModel


class MultiModalPageEmbeddingMeta(BaseModel):
    """Metadata for a multi modal embedding output."""

    embedding: bytes
