from __future__ import annotations
import logging
from sentence_transformers import sentence_transformer

logger = logging.getLogger(__name__)


class BgeSmall:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        logger.info(f"Initializing model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Model intialized Sucessfully")
            self._encode_sync("Warm Up")
        except Exception as e:
            logger.error(f"Failed to initialized model: {model_name}. Error: {e}")
            raise

    def _encode_sync(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )
        embedding = embedding.tolist()
        self.vector_size = len(embedding)
        return embedding
    
    async def get_embedding_size(self) -> int:
        return self.vector_size
    
    async def get_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            logger.warning("Recieved empty string for embedding generation.")
            return []

        try:
            embedding = await asyncio.to_thread(self._encode_sync, text)
            return embedding
        
        except Exception as e:
            logger.error(f"Failed to generate embedding for Text: {text[:50]},  Error: {e}")
            raise

        