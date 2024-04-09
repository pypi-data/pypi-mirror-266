"""Classifier Resource Module."""

from typing import List, Literal, Optional, Union

from ..dataclasses.classify import Classification, ClassifierMeta
from .base import AsyncResource, SyncResource


class SyncClassifierResource(SyncResource):
    """Synchronous Classififer Resource Class."""

    def classify(
        self,
        text: str,
        task: Union[Literal["zero-shot-classification"], Literal["text-classification"]],
        labels: Optional[List[str]] = None,
        priority: int = 0,
    ) -> ClassifierMeta:
        """Embed all texts."""
        input_data = {"text": text}
        if task == "zero-shot-classification":
            input_data["candidate_labels"] = labels
        output = self._post(
            data={
                "input_data": input_data,
                "task": task,
                "priority": priority,
            },
        )
        output.raise_for_status()
        classification_resp = output.json()["output"]
        labels = classification_resp["labels"]
        scores = classification_resp["scores"]
        return ClassifierMeta(
            classifications=[
                Classification(label=label, confidence=score)
                for label, score in zip(labels, scores)
            ],
            text=text,
        )


class AsyncClassifierResource(AsyncResource):
    """Asynchronous Classifier Resource Class."""

    async def classify(
        self,
        text: str,
        task: Union[Literal["zero-shot-classification"], Literal["text-classification"]],
        labels: Optional[List[str]] = None,
        read_timeout: float = 10.0,
        timeout: float = 180.0,
        priority: int = 0,
    ) -> ClassifierMeta:
        """Embed all texts."""
        input_data = {"text": text}
        if task == "zero-shot-classification":
            input_data["candidate_labels"] = labels
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
        classification_resp = output.json()["output"]
        labels = classification_resp["labels"]
        scores = classification_resp["scores"]
        return ClassifierMeta(
            classifications=[
                Classification(label=label, confidence=score)
                for label, score in zip(labels, scores)
            ],
            text=text,
        )
