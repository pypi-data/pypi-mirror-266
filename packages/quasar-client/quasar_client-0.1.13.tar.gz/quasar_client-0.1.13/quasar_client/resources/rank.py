"""Ranker Resource Module."""

from typing import List, Tuple

from ..dataclasses.rank import RankerMeta
from .base import AsyncResource, SyncResource


class SyncRankerResource(SyncResource):
    """Synchronous Ranker Resource Class."""

    def rank(
        self,
        pairs: List[Tuple[str, str]],
        priority: int = 0,
    ) -> List[RankerMeta]:
        """Rank pairs of text."""
        output = self._post(
            data={
                "input_data": {"pairs": pairs},
                "task": "ranking",
                "priority": priority,
            },
        )
        output.raise_for_status()
        return [
            RankerMeta(
                pair=(pair["query"], pair["candidate"]),
                score=pair["score"],
            )
            for pair in output.json()["output"]
        ]


class AsyncRankerResource(AsyncResource):
    """Asynchronous Ranker Resource Class."""

    async def rank(
        self,
        pairs: List[Tuple[str, str]],
        read_timeout: float = 10.0,
        timeout: float = 180.0,
        priority: int = 0,
    ) -> List[RankerMeta]:
        """Asynchronously rank pairs of text."""
        response = await self._post(
            data={
                "input_data": {"pairs": pairs},
                "task": "ranking",
                "priority": priority,
            },
            read_timeout=read_timeout,
            timeout=timeout,
        )
        response.raise_for_status()
        return [
            RankerMeta(
                pair=(pair["query"], pair["candidate"]),
                score=pair["score"],
            )
            for pair in response.json()["output"]
        ]
