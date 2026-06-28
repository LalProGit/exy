import logging
from pydantic import BaseModel, Field
from typing import Callable, Awaitable, Any, Protocol

logger = logging.getLogger(__name__)

class ToolManifest(BaseModel):
    name: str 
    description: str
    callable_func: Callable[..., Awaitable[Any]]


class ToolsRegistry(Protocol):
    async def get_relevant_tools(self, intent: str) -> list[ToolManifest]:
        ...


class EmbeddingProvider(Protocol):
    async def get_embedding(self, text:str) -> list[float]:
        ...

    async def get_embedding_size(self) -> int:
        ...
