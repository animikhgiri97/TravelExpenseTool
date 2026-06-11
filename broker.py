import asyncio
from typing import Callable, Dict, List, Any


class Broker:
    def __init__(self):
        self._handlers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}

    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], Any]):
        """Register an async handler for a channel."""
        self._handlers.setdefault(channel, []).append(handler)

    async def request(self, channel: str, message: Dict[str, Any], timeout: float | None = None):
        """Send a request to a channel and await handler response.

        Returns the first non-None handler result.
        """
        handlers = self._handlers.get(channel, [])
        if not handlers:
            raise RuntimeError(f"No handlers subscribed to channel '{channel}'")

        # Call handlers sequentially and return first non-None response
        for h in handlers:
            try:
                coro = h(message)
                if not asyncio.iscoroutine(coro):
                    # handler might be sync
                    res = coro
                else:
                    if timeout:
                        res = await asyncio.wait_for(coro, timeout=timeout)
                    else:
                        res = await coro
                if res is not None:
                    return res
            except Exception:
                continue

        return None
