"""Dataclasses for embeddings."""
from typing import Dict, List
from pydantic import BaseModel


class LayoutElementClassifierMeta(BaseModel):
    """Metadata for a multi modal embedding output."""

    classified_blocks_by_page: Dict[int, List[dict]]