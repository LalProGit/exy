from __future__ import annotations
import logging
import asyncio
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class BgeSmall:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        logger.info(f"Initializing model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Model initialized successfully")
            # Warm up once to establish vector size
            self._encode_sync("Warm Up")
        except Exception as e:
            logger.error(f"Failed to initialize model: {model_name}. Error: {e}")
            raise

    def _encode_sync(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )
        # SentenceTransformer returns numpy arrays; convert to python list
        try:
            embedding_list = embedding.tolist()
        except Exception:
            embedding_list = list(embedding)

        self.vector_size = len(embedding_list)
        return embedding_list

    async def get_embedding_size(self) -> int:
        return getattr(self, "vector_size", 0)

    async def get_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            logger.warning("Received empty string for embedding generation.")
            return []

        try:
            embedding = await asyncio.to_thread(self._encode_sync, text)
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding for Text: {text[:50]},  Error: {e}")
            raise
        
