from urllib3 import Retry as __retry__

from ._Requests import RequestsAdapter

class Retry:

    def __new__(cls) -> '__retry__':
        return __retry__(
            total=3,
            status_forcelist=[104, 429, 500, 502, 503, 504],
            backoff_factor=2
        )

__all__ = [
    'RequestsAdapter',
    'Retry',
]