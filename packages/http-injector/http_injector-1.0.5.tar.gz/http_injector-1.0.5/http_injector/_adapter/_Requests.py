from typing import Any
import ssl
import requests

from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager  # type: ignore
from urllib3.util import ssl_

from .._context import SSLContext, MY_CHIPER

class RequestsAdapter(HTTPAdapter):
    
    def __init__(self, timeout=None, *args, **kwargs):
        self.timeout = timeout
        if "timeout" in kwargs:
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)
    
    """TLS tweaks."""

    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        """
        Secure settings from ssl.create_default_context(), but without
        ssl.OP_NO_TICKET which causes Google to return 403 Bad
        Authentication.
        """
        context = SSLContext()
        context.set_ciphers(MY_CHIPER)
        #context.set_alpn_protocols(ssl.PROTOCOL_SSLv23)
        #context.verify_mode = ssl.CERT_REQUIRED
        context.options &= ~ssl.OP_NO_TICKET  # pylint: disable=E1101
        self.poolmanager = PoolManager(*args, ssl_context=context, **kwargs)
