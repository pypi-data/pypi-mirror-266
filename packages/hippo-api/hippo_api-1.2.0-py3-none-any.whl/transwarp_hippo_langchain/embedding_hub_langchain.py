from __future__ import annotations

import logging
from typing import (
    Any,
    List,
)

from pydantic import BaseModel

from transwarp_embedding_hub.embedding_hub import *

from langchain.embeddings.base import Embeddings

logger = logging.getLogger(__name__)


class TranswarpEmbeddingHub(BaseModel, Embeddings):
    """embedding hub intergration hippo_with_langchain"""

    model: str
    strategy: Any

    # Initialize strategy based on model name
    def __init__(self, **data: Any):
        super().__init__(**data)
        self.strategy = EmbeddingHub(self.model).get_strategy()

    # Check if the model is available
    def check_model_active(self):
        try:
            self.embed_query("你好")
            return True
        except Exception as e:
            print(f"Model not available. Error: {e}")
            return False

    # Convert documents to a set of vectors
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        list = []
        for text in texts:
            list.append(self.strategy.embed_string(text))
        return list

    # Convert string to vector
    def embed_query(self, text: str) -> List[float]:
        return self.strategy.embed_string(text)
