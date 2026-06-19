from __future__ import annotations
from typing import Protocol

class SecurityProvider(Protocol):
    """ Abstract interface for all authentication mechanisms. """
    def verify(self, user_id: str) -> bool:

class DiscordOwnerSecurity:
    """ Discord owner-based authentication. """

    def __init__(self, owner_ids: list[str]):
        self.owner_ids = set(owner_ids)

    def verify(self, user_id: str) -> bool:

        if(user_id not in self.owner_ids):
            logger.warning(f"Unauthorized access attempt by user_id: {user_id}")
            return False

        return True
    
