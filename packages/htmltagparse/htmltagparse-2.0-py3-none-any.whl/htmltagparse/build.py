from .parser import HtmlPage
import requests
import time
from .exceptions import *

__all__ = [
    "fromUri",
]

def fromUri(uri: str, timeout=5, headers={}) -> object:
    """Builds an html page from a URI."""
    priorEpoch = time.time()
    try:
        resp = requests.get(uri, timeout=timeout, headers=headers)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
        raise HtmlHttpError("did not receive server data within timeout duration")
    tagTimeout = timeout - (time.time() - priorEpoch)
    pageHtml = resp.text
    page = HtmlPage(pageHtml, timeout=tagTimeout)
    page.uri = resp.url
    page.response = (resp.status_code, resp.reason)
    page.elapsed = time.time() - priorEpoch
    return page
