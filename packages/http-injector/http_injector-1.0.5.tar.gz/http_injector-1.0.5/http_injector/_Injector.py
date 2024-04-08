from enum import Enum, auto
from typing import Dict, Optional, Union

from httpx import Client
from requests import Session

from ._Requests import Adapter as _RAdapter
from ._Httpx import Adapter as _HAdapter

class TypeInjector(Enum):

    requests = auto()
    httpx = auto()

class ProxyType(Enum):
    
    socks5  = auto()
    http    = auto()

class ProxyParams:

    URL: str = None

    def __new__(cls, type: ProxyType, IP: str, PORT: int, USERNAME: Optional[str] = None, PASSWORD: Optional[str] = None) -> 'ProxyParams':
        if USERNAME is not None and PASSWORD is not None:
            build = f'{USERNAME}:{PASSWORD}@{IP}:{PORT}'
        else:
            build = f'{IP}:{PORT}'
        if type == ProxyType.http:
            setattr(ProxyParams, 'URL', f'http://{build}')
        elif type == ProxyType.socks5:
            setattr(ProxyParams, 'URL', f'socks5://{build}')
        return cls

class HTTPInjector(_HAdapter, _RAdapter):

    def __new__(cls, typeInjector: TypeInjector, timeout: int = 30, headers: Dict[str, str] = dict(), proxyParams: Optional[ProxyParams] = None) -> Union[Client, Session]:
        if not proxyParams:
            proxy_url = None
        else:
            proxy_url = proxyParams.URL
        if typeInjector == TypeInjector.requests:
            return _RAdapter.__new__(cls, timeout, headers, proxy_url)
        elif typeInjector == TypeInjector.httpx:
            return _HAdapter.__new__(cls, timeout, headers, proxy_url)