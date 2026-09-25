"""
Base Worker Interface for Aether Engine
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseWorker(ABC):
    """Abstract Base Class for Task Execution Workers."""

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes task payload and returns result dictionary."""
        pass
