from __future__ import annotations
import asyncio
import logging
from typing import Any

from fastapi import Request

from src.domain.db.database import DatabaseManager
from src.domain.tools.local.local_registry import LocalSQLiteRegistry
from src.domain.tools.embedding.embedding_providers import BgeSmall
import src.domain.tools.local.my_tools  

logger = logging.getLogger(__name__)


async def initialize_registries(app) -> None:
    """Create DB, embedding provider and registries and attach to app.state."""
    db = DatabaseManager("tools.db")

    embedder = await asyncio.to_thread(BgeSmall)
    logger.info("Initialized embedding provider")

    local_registry = LocalSQLiteRegistry(db_manager=db, embedder=embedder)

    await local_registry.initialize()

    app.state.tool_registry = local_registry


def get_tool_registry(request: Request) -> Any:
    return request.app.state.tool_registry


__all__ = ["initialize_registries", "get_tool_registry"]
