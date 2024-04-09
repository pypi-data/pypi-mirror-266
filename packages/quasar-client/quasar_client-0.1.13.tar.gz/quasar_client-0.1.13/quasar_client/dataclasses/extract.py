"""Dataclasses for extractions."""

from typing import List, Optional

from pydantic import BaseModel


class Keyword(BaseModel):
    """Keyword dataclass."""

    keyword: str
    score: float


class ExtractMeta(BaseModel):
    """Metadata for an extractor output."""

    text: str
    keywords: Optional[List[Keyword]] = None
    topics: Optional[List[str]] = None
