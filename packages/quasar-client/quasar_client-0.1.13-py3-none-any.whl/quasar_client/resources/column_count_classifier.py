"""Classifier Resource Module."""

from typing import List

from ..dataclasses.column_count_classifier import ColumnCountClassifierMeta
from .base import AsyncResource, SyncResource


class SyncLayoutElementClassifierResource(SyncResource):
    """Synchronous Classififer Resource Class."""

    def classify(
        self,
        pages_images_base64_string: str,
        bboxes: List, 
        words: List,
    ) -> ColumnCountClassifierMeta:
        
        """Column classification of every page"""
        task = "column-count-classification"
        input_data = {
                "pages_images_base64_string": pages_images_base64_string, 
                "bboxes": bboxes, 
                "words": words}
        
        output = self._post(
            data={
                "input_data": input_data,
                "task": task,
            },
        )
        
        output.raise_for_status()
        return ColumnCountClassifierMeta(
            column_counts=output.json()["output"]
        )


class AsyncLayoutElementClassifierResource(AsyncResource):
    """Asynchronous Classifier Resource Class."""

    async def classify(
        self,
        pages_images_base64_string: str,
        bboxes: List, 
        words: List,
        read_timeout: float = 10.0,
        timeout: float = 180.0,
    ) -> ColumnCountClassifierMeta:
        """Embed all texts."""
        task = "column-count-classification"
        input_data = {
                "pages_images_base64_string": pages_images_base64_string, 
                "bboxes": bboxes, 
                "words": words}
            
        output = await self._post(
            data={
                "input_data": input_data,
                "task": task,
            },
            read_timeout=read_timeout,
            timeout=timeout
        )
        
        output.raise_for_status()
        return ColumnCountClassifierMeta(
            column_counts=output.json()["output"]
        )