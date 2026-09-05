import logging
from typing import Protocol
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from fastapi import Depends

from src.core.config import get_settings
from src.domain.ingress.schema import ExyPayload
from src.domain.tools.tool import get_tool_registry
from src.domain.tools.global_tool_registry import GlobalToolRegistry

logger = logging.getLogger(__name__)
class ExyAgentCore:
    "Orchestrator Engine"

    def __init__(self, model: OpenAIModel, tools_registry: GlobalToolRegistry):
        self.model = model
        self.tools_registry = tools_registry
        self.system_prompt = (Path(__file__).parent / "prompts" / "system_prompt.txt").read_text()

    async def process_intent(self, payload: ExyPayload) -> str:
        logger.info(f"Orchestrator analyzing intent: {payload.raw_text}")
        
        # Later add if startswith("/") to handle direct commands

        agent = Agent(
            model = self.model,
            system_prompt = self.system_prompt,
        )

        relevant_tools = await self.tools_registry.get_relevant_tools(intent=payload.raw_text, top_k = 5)

        for tool in relevant_tools:
            agent.tool_plain(name=tool.name, description=tool.description)(tool.callable_func)
            logger.info(f"Injected tool: {tool.name}")
        
        try:
            logger.info("Executing LLM with tools")
            result = await agent.run(payload.raw_text)
            return result.output
        except Exception as e:
            logger.error(f"Agent Core Exception: {e}")
            return "System Fault: Orchestrator failed to return the result"
             
def get_orchestrator(
    tools_registry: GlobalToolRegistry = Depends(get_tool_registry)
) -> ExyAgentCore:
    """Factory to construct the orchestrator and inject"""

    settings = get_settings()
    provider = OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key=settings.openrouter_api_key,
    )
    model = OpenAIModel(
        model_name='openrouter/free',
        provider=provider,
    )

    return ExyAgentCore(model=model, tools_registry=tools_registry)
