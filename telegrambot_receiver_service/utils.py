import asyncio
from typing import Union

import netaddr

from uuid import uuid4


def get_uuid():
    return str(uuid4())


def async_gather(*coroutines):
    async def __f():
        return await asyncio.gather(*coroutines)

    return asyncio.run(__f())


def ip_in_network(ip: str, network: Union[str, netaddr.IPNetwork]) -> bool:
    ip = netaddr.IPAddress(ip)
    network = netaddr.IPNetwork(network) if isinstance(network, str) else network
    return ip in network
