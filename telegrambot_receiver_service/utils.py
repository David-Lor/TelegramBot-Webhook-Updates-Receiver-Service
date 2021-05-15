import asyncio
from typing import Union, Optional

import netaddr

from uuid import uuid4


def get_uuid():
    return str(uuid4())


def async_gather(*coroutines, timeout: Optional[float] = None):
    async def __f():
        coro = asyncio.gather(*coroutines)
        if timeout is not None:
            return await asyncio.wait_for(coro, timeout=timeout)
        return await coro

    return asyncio.get_event_loop().run_until_complete(__f())


def ip_in_network(ip: str, network: Union[str, netaddr.IPNetwork]) -> bool:
    ip = netaddr.IPAddress(ip)
    network = netaddr.IPNetwork(network) if isinstance(network, str) else network
    return ip in network
