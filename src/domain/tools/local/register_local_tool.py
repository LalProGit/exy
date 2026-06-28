from __future__ import annotations
from typing import Any, Callable, Awaitable

_GLOBAL_TOOL_REGISTRY: dict[str, dict[str, Any]] = {}

def register_local_tool(name: str, description: str):
    """
        Decorater to registring tools
    """
    def decorater(func: Callable[..., Awaitable[Any]]):
        callable_name = func.__name__

        _GLOBAL_TOOL_REGISTRY[callable_name] = dict(
            name: name,
            func: func,
            description: description
        )
        return func
    
    return decorater

            
