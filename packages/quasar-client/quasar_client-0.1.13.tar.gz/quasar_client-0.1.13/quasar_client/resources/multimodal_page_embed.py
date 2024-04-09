"""Ranker Resource Module."""

from ..dataclasses.multimodal_page_embed import MultiModalPageEmbeddingMeta
from .base import AsyncResource, SyncResource


class SyncMultiModalPageEmbeddingResource(SyncResource):
    """Synchronous Embedding Resource Class."""

    def embed(
        self,
        page_properties: dict,
    ):
        """Encode the entire page using Multimodal models"""
        task = "mm-page-embedding"
        input_data = {"page_properties": page_properties}
        
        output = self._post(
            data={
                "input_data": input_data,
                "task": task,
            },
        )
        output.raise_for_status()
        
        return MultiModalPageEmbeddingMeta(embedding=output.content)


class AsyncMultiModalPageEmbeddingResource(AsyncResource):
    """Asynchronous Embedding Resource Class."""

    async def embed(
        self,
        page_properties: str,
        read_timeout: float = 10.0,
        timeout: float = 180.0,
    ):
        """Asynchronously embed all pages via multimodal."""
        task = "mm-page-embedding"
        input_data = {"page_properties": page_properties}
        
        output = await self._post(
             data={
                "input_data": input_data,
                "task": task,
            },
            read_timeout=read_timeout,
            timeout=timeout,
        )
        output.raise_for_status()  # Ensure proper exception handling in your async context.
        return MultiModalPageEmbeddingMeta(embedding=output.content)
