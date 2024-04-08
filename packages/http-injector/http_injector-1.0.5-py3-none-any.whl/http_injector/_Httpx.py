import ssl
from typing import Dict, Optional
import chardet
import httpx
from httpx import Client

from ._context import SSLContext, MY_CHIPER, certificate
from ._utils import raise_on_4xx_5xx

class Adapter:

    @staticmethod
    def __autodetect__(content):
        return chardet.detect(content).get('encoding')
    
    def __new__(cls, timeout: int, headers: Dict[str, str], proxy_url: Optional[str] = None) -> Client:
        context = SSLContext()
        context.set_ciphers(MY_CHIPER)
        context.options &= ~ssl.OP_NO_TICKET  # pylint: disable=E1101
        context.load_verify_locations(cafile=certificate())
        timeouts    = httpx.Timeout(float(timeout), connect=60.0)
        transport   = httpx.HTTPTransport(http2=True, retries=3.0)
        header: Dict[str, str] = dict()
        for k, v in zip(headers.keys(), headers.values()): header.update(**{k.lower():v})
        if not header.get('User-Agent'.lower()):
            VERSION = 1.0
            header.update(**{'User-Agent'.lower() : 'des-scrypt/{}'.format(VERSION)})
        return httpx.Client(http2=True, cert=context, verify=context, proxies=proxy_url, headers=header, default_encoding=cls.__autodetect__, timeout=timeouts, transport=transport)