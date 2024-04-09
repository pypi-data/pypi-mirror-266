"""Extract Resource Module."""

from typing import List, Literal, Optional, Union

from ..dataclasses.extract import ExtractMeta, Keyword
from .base import AsyncResource, SyncResource


class SyncExtractorResource(SyncResource):
    """Synchronous ExtractorResource Class."""

    def extract(
        self,
        text: str,
        task: Union[Literal["topics"], Literal["keyword-extraction"]],
        priority: int = 0,
        **kwargs,
    ) -> ExtractMeta:
        """Extract keywords or topics."""
        input_data = {"docs": [text], **kwargs}
        output = self._post(
            data={
                "input_data": input_data,
                "task": task,
                "priority": priority,
            },
        )
        output.raise_for_status()
        extract_response = output.json()["output"]
        return ExtractMeta(
            text=text,
            keywords=[
                Keyword(
                    keyword=kw["keyword"],
                    score=kw["score"],
                )
                for kw in extract_response[0]["keywords"]
            ],
        )


class AsyncExtractorResource(AsyncResource):
    """Asynchronous Extractor Resource Class."""

    async def extract(
        self,
        text: str,
        task: Union[Literal["topics"], Literal["keyword-extraction"]],
        read_timeout: float = 10.0,
        timeout: float = 180.0,
        priority: int = 0,
        **kwargs,
    ) -> ExtractMeta:
        """Extract keywords or topics."""
        input_data = {"docs": [text], **kwargs}
        output = await self._post(
            data={
                "input_data": input_data,
                "task": task,
                "priority": priority,
            },
            read_timeout=read_timeout,
            timeout=timeout,
        )
        output.raise_for_status()
        extract_response = output.json()["output"]
        return ExtractMeta(
            text=text,
            keywords=[
                Keyword(
                    keyword=kw["keyword"],
                    score=kw["score"],
                )
                for kw in extract_response[0]["keywords"]
            ],
        )
