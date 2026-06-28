from __future__ import annotations
from src.domain.tools.local.register_local_tool import register_local_tool

@register_local_tool(
    name="boss_name",
    description="Return the name of your boss, or who owns you and made you"
)
async def boss_name(**kwargs) -> str:
    return "You are Made by Prabhakar (ghost) Lal"

