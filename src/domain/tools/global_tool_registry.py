import logging
import asyncio
from src.domain.tools.models import ToolsRegistry, ToolManifest

logger = logging.getLogger(__name__)

class GlobalToolRegistry:
    def __init__(self, registries: list[ToolsRegistry]):
        self._registries = registries

    async def get_relevant_tools(self, intent: str, top_k: int = 3) -> list[ToolManifest]:
        # Query all registries in parallel, suppressing failures from offline servers
        results = await asyncio.gather(
            *[registry.get_relevant_tools(intent, top_k=top_k) for registry in self._registries],
            return_exceptions=True
        )

        aggregated_tools = []
        seen_names = set()

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"⚠️ Registry {self._registries[idx].__class__.__name__} failed: {result}")
                continue
                
            for tool in result:
                if tool.name not in seen_names:
                    seen_names.add(tool.name)
                    aggregated_tools.append(tool)

        return aggregated_tools