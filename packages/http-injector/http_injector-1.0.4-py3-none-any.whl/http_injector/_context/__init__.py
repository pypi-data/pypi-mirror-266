import ssl
import httpx
import importlib.resources as pkg_resources

from .SSLContext import SSLContext
from .CIPHERS import MY_CHIPER

from .._utils import _certificate

def certificate():
    with pkg_resources.path(_certificate, 'cacert.pem') as p:
        return str(p)