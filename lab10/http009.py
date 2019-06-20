import io
import os
import socket
import http.client

from urllib.parse import urlparse


def http_response(url):
    """
    Opens a request to the given URL using the `http.client` library.

    Parameters:
        url (str or bytes):
            The URL containing the resource to be downloaded

    Rerturns:
        A file-like object representing the response received from the server.
        In the case of http:// or https:// requests, the return value will be
        an instance of `http.client.HTTPResponse`.  In the case of a file://
        request (representing a local file on disk), the return value will be
        an `io.BytesIO` object.

        In either case, the returned object will support `read` and `readlines`,
        and it will have a `status` attribute containing an HTTP status code.
    """
    if isinstance(url, bytes):
        url = url.decode('utf-8')
    url = urlparse(url)
    assert url.scheme in ('http', 'file', 'https')
    if url.scheme == 'file':
        fname = os.path.join(url.netloc, url.path)
        if os.path.isfile(fname):
            out = open(fname, 'rb')
            out.status = 200
        else:
            out = io.BytesIO()
            out.status = 404
        return out
    cls = http.client.HTTPConnection if url.scheme == 'http' else http.client.HTTPSConnection
    try:
        connection = cls(url.netloc, timeout=20)
        connection.request('GET', url.path)
    except socket.timeout:
        raise ConnectionError('no response from server within 5 seconds; connection attempt timed out') from None
    except socket.gaierror:
        raise ConnectionError('could not connect') from None
    return connection.getresponse()
