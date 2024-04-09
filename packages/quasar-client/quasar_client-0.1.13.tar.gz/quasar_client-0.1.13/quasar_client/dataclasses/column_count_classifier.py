"""Dataclasses for embeddings."""
from typing import List
from pydantic import BaseModel


class ColumnCountClassifierMeta(BaseModel):
    """Metadata for a multi modal embedding output."""

    column_counts: List[int]