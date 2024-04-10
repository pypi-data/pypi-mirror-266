# coding=utf-8

"""
@fileName       :   http_client.py
@data           :   2024/2/28
@author         :   jiangmenggui@hosonsoft.com
"""
from urllib.parse import urlparse
from http.client import HTTPConnection


class HTTPClient:

    def __init__(self, base_url: str = '', timeout=60):
        url = urlparse(base_url)
        self._timeout = timeout
        self._pool = {}


if __name__ == '__main__':
    pass
