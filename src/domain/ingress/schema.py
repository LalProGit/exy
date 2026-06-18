from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class ExyPayload(BaseModel):
    """
    ExyP payload schema.
    """
    user_id: str = Field(..., description="Unique identifier for the user.")
    platform: Literal['discord', 'whatsapp', 'telegram'] = Field(..., description="Source of message.")
    raw_text: str = Field(..., description="Original message text.")
    timestamp: int = Field(..., description="Unix timestamp of when the message was sent.")
    message_id: str = Field(..., description="Unique tracking identifier.")
    channel_id: str = Field(..., description="Target execution room context.")    

