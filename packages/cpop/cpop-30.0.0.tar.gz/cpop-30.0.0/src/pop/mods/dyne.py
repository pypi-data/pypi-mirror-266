from typing import Any


async def get(hub: "pop.hub.Hub") -> dict[str, Any]:
    """
    Retrive the dynamic dirs data for this hub, if dynamic dirs have not been
    gathered yet then gather it.
    """
    return hub._dynamic.dyne
