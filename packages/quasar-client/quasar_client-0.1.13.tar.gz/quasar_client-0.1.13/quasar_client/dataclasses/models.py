"""Dataclasses for Quasar."""

from typing import Dict, Optional

from pydantic import BaseModel


class ModelData(BaseModel):
    """Model data from Quasar."""

    id: str
    provider: str
    metadata: Optional[Dict]
