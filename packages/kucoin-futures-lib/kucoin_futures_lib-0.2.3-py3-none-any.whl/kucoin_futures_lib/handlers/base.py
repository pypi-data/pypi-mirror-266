"""Abstract Base Class for Handlers."""

import asyncio
from abc import ABC, abstractmethod
from typing import Union


class HandlerABC(ABC):
    """Handler Abstract Base˙ Class"""

    @property
    @abstractmethod
    def done(self) -> asyncio.Event:
        """Return the done status for the handler."""
        raise NotImplementedError("Done method not implemented")

    @property
    @abstractmethod
    def topic(self) -> str:
        """Return the topic supported by the handler."""
        raise NotImplementedError("Topic method not implemented")

    @property
    @abstractmethod
    def private(self) -> bool:
        """Return the privacy status for the topic."""
        raise NotImplementedError("Privacy method not implemented")

    @abstractmethod
    async def handle(self, msg: Union[dict, list]):
        """Handle method that will be called by the WebSocket client."""
        raise NotImplementedError("Handle method not implemented")
