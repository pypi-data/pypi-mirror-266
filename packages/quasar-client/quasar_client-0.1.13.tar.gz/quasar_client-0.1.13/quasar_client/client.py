"""Quasar client: inference, training, etc."""

from typing import List
from urllib.parse import urljoin

import requests
from openai import AsyncOpenAI, OpenAI

from .dataclasses.models import ModelData
from .resources.classifier import AsyncClassifierResource, SyncClassifierResource
from .resources.coref import AsyncCorefResource, SyncCorefResource
from .resources.embed import AsyncEmbeddingResource, SyncEmbeddingResource
from .resources.extract import AsyncExtractorResource, SyncExtractorResource
from .resources.layout_element_classifier import (
    AsyncLayoutElementClassifierResource,
    SyncLayoutElementClassifierResource,
)
from .resources.multimodal_page_embed import (
    AsyncMultiModalPageEmbeddingResource,
    SyncMultiModalPageEmbeddingResource,
)
from .resources.rank import AsyncRankerResource, SyncRankerResource
from .resources.tagger import AsyncTaggerResource, SyncTaggerResource


class Quasar(OpenAI):
    """Quasar Client"""

    classifier: SyncClassifierResource
    coref: SyncCorefResource
    embed: SyncEmbeddingResource
    extractor: SyncExtractorResource
    ranker: SyncRankerResource
    tagger: SyncTaggerResource
    layout_element_classifier: SyncLayoutElementClassifierResource
    multimodal_page_embed: SyncMultiModalPageEmbeddingResource

    def __init__(self, quasar_base: str, *args, **kwargs) -> None:
        """Construct an inference client to Quasar."""
        self.quasar_base = quasar_base
        self._models: List[ModelData] = []
        kwargs["api_key"] = "EMPTY"
        # Set OpenAI base_url for OpenAI-compatible methods
        kwargs["base_url"] = urljoin(self.quasar_base, "/predictions/v1")
        super().__init__(*args, **kwargs)
        self.classifier = SyncClassifierResource(self.quasar_base)
        self.coref = SyncCorefResource(self.quasar_base)
        self.embed = SyncEmbeddingResource(self.quasar_base)
        self.extractor = SyncExtractorResource(self.quasar_base)
        self.ranker = SyncRankerResource(self.quasar_base)
        self.tagger = SyncTaggerResource(self.quasar_base)
        self.layout_element_classifier = SyncLayoutElementClassifierResource(self.quasar_base)
        self.multimodal_page_embed = SyncMultiModalPageEmbeddingResource(self.quasar_base)

    def list_models(self, use_cache: bool = False) -> List[ModelData]:
        """Get all models callable within Quasar and cache them."""
        # Early exit to use cache
        if use_cache and self._models:
            return self._models
        list_models_endpoint = urljoin(self.quasar_base, "predictions/v1/models")
        response = requests.get(list_models_endpoint)
        response.raise_for_status()
        models_data = response.json()
        all_models_info = []
        for provider, models in models_data.items():
            for model in models:
                model_id = model.pop("id", None) or model.pop("model", None)
                metadata = model.pop("metadata", {})
                all_models_info.append(
                    ModelData(
                        id=model_id,
                        provider=provider,
                        metadata=metadata,
                    )
                )
        self._models = all_models_info
        return all_models_info

    def list_model_info(self, model_id: str) -> ModelData:
        """List model info."""
        for model in self.list_models(use_cache=True):
            if model.id == model_id:
                return model
        raise ValueError(f"Quasar Model Information {model_id} not found.")


class AsyncQuasar(AsyncOpenAI):
    """Quasar Async Client"""

    classifier: AsyncClassifierResource
    coref: AsyncCorefResource
    embed: AsyncEmbeddingResource
    extractor: AsyncExtractorResource
    ranker: AsyncRankerResource
    tagger: AsyncTaggerResource
    layout_element_classifier: AsyncLayoutElementClassifierResource
    multimodal_page_embed: AsyncMultiModalPageEmbeddingResource

    def __init__(self, quasar_base: str, *args, **kwargs) -> None:
        """Construct an inference client to Quasar."""
        self.quasar_base = quasar_base
        self._models: List[ModelData] = []
        kwargs["api_key"] = "EMPTY"
        # Set OpenAI base_url for OpenAI-compatible methods
        kwargs["base_url"] = urljoin(self.quasar_base, "/predictions/v1")
        super().__init__(*args, **kwargs)
        self.classifier = AsyncClassifierResource(self.quasar_base)
        self.coref = AsyncCorefResource(self.quasar_base)
        self.embed = AsyncEmbeddingResource(self.quasar_base)
        self.extractor = AsyncExtractorResource(self.quasar_base)
        self.ranker = AsyncRankerResource(self.quasar_base)
        self.tagger = AsyncTaggerResource(self.quasar_base)
        self.layout_element_classifier = AsyncLayoutElementClassifierResource(self.quasar_base)
        self.multimodal_page_embed = AsyncMultiModalPageEmbeddingResource(self.quasar_base)

    def list_models(self, use_cache: bool = False) -> List[ModelData]:
        """Get all models callable within Quasar and cache them."""
        # Early exit to use cache
        if use_cache and self._models:
            return self._models
        list_models_endpoint = urljoin(self.quasar_base, "predictions/v1/models")
        response = requests.get(list_models_endpoint)
        response.raise_for_status()
        models_data = response.json()
        all_models_info = []
        for provider, models in models_data.items():
            for model in models:
                model_id = model.pop("id", None) or model.pop("model", None)
                metadata = model.pop("metadata", {})
                all_models_info.append(
                    ModelData(
                        id=model_id,
                        provider=provider,
                        metadata=metadata,
                    )
                )
        self._models = all_models_info
        return all_models_info

    def list_model_info(self, model_id: str) -> ModelData:
        """List model info."""
        for model in self.list_models(use_cache=True):
            if model.id == model_id:
                return model
        raise ValueError(f"Quasar Model Information {model_id} not found.")
