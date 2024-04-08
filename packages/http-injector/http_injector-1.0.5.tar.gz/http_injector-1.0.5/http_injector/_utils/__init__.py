from typing import Union

from httpx import Response as HResponse
from requests import Response as RResponse

def raise_on_4xx_5xx(response: Union[HResponse, RResponse]):
    response.raise_for_status()
    