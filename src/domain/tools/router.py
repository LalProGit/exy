from __future__ import annotations
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.domain.tools.bootstrap import get_tool_registry
from src.domain.tools.models import ToolManifest

router = APIRouter(tags=["Tools"])


@router.get("/tools")
async def get_tools(
	intent: str = Query(..., description="Intent or query to find tools for"),
	top_k: int = Query(3, ge=1, description="Maximum number of tools to return"),
	registry: Any = Depends(get_tool_registry),
):
	"""Return relevant tools for a given intent using the registered tool registry."""
	try:
		manifests: list[ToolManifest] = await registry.get_relevant_tools(intent, top_k=top_k)
	except TypeError:
		# Some registries implement get_relevant_tools(intent) without top_k
		manifests = await registry.get_relevant_tools(intent)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

	return [{"name": m.name, "description": m.description} for m in manifests]
     