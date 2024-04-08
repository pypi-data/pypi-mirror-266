from typing import Dict, Optional
from requests import Session

from ._adapter import Retry, RequestsAdapter
from ._utils import raise_on_4xx_5xx

class Adapter:

    def __new__(cls, timeout: int, headers: Dict[str, str], proxy_url: Optional[str] = None) -> 'Session':
        requests = Session()
        adapter = RequestsAdapter(timeout=timeout, max_retries=Retry)
        for scheme in ('http://', 'https://'): requests.mount(scheme, adapter)
        if not proxy_url:
            requests.proxies = dict()
        else:
            requests.proxies = dict(http = proxy_url, https = proxy_url)
        requests.headers.update(**headers)
        return requests