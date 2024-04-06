import aiohttp_socks
import json as jsons
from aiohttp import ClientSession, ClientTimeout

#Aiow
class Aiow:
    """Aiow Class

    Aiohttp based wrapper.

    Usage:
      - Get request: await Aiow.Get(args)
      - Post request: await Aiow.Post(args)
    """

    # Post aiohttp
    @classmethod
    async def Post(cls, url: str, asjson=True, headers=None, json=None, data=None, params=None, cookie=None, timeout=100, proxy=None):
        """
        Post request: await Aiow.Post()
        :param url:
        :param asjson:
        :param headers:
        :param json:
        :param data:
        :param params:
        :param cookie:
        :param timeout:
        :param proxy:
        :return: json if asjson==True else text:
        """
        time_out = ClientTimeout(total=timeout)
        set_proxy = aiohttp_socks.ProxyConnector.from_url(proxy) if proxy else None
        async with ClientSession(timeout=time_out, connector=set_proxy, cookies=cookie) as session:
            async with session.post(url, headers=headers, json=json, data=data, params=params) as resp:
                if asjson:
                    return jsons.loads(await resp.text())
                else:
                    return await resp.text()

    #Get aiohttp
    @classmethod
    async def Get(cls, url: str, asjson=True, headers=None, json=None, data=None, params=None, cookie=None, timeout=100, proxy=None):
        """
        Get request: await Aiow.Get()
        :param url:
        :param asjson:
        :param headers:
        :param json:
        :param data:
        :param params:
        :param cookie:
        :param timeout:
        :param proxy:
        :return: json if asjson==True else text:
        """
        time_out = ClientTimeout(total=timeout)
        set_proxy = aiohttp_socks.ProxyConnector.from_url(proxy) if proxy else None
        async with ClientSession(timeout=time_out, connector=set_proxy, cookies=cookie) as session:
            async with session.get(url, headers=headers, json=json, data=data, params=params) as resp:
                if asjson:
                    return jsons.loads(await resp.text())
                else:
                    return await resp.text()
