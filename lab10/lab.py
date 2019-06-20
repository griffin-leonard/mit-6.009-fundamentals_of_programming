import sys
import doctest
from http009 import http_response

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!

CHUNK_SIZE = 8192


def download_file(loc, cache=None):
    """
    Yield the raw data from the given URL, in segments of CHUNK_SIZE bytes.

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises a RuntimeError if the URL can't be reached, or in the case of a 500
    status code.  Raises a FileNotFoundError in the case of a 404 status code.
    """
    # Try implementing cache as dictionary mapping "url" -> file data

    # Hint: consider making another function to handle manifests
    # Hint: b''.decode("utf-8") decodes a bytestring to a python string
    #       use this when deciding what URLs in the manifest to download again
    try:
        r = http_response(loc)
    except: #no response
        raise RuntimeError
    
    status = r.status
    if status == 404: #404 errors
        raise FileNotFoundError
    elif status == 500: #500 errors
        raise RuntimeError
    elif status in (301, 302, 307): #redirects
        header = r.getheader('location')
        for l in download_file(header):
            yield l
    elif r.getheader('content-type') == 'text/parts-manifest' or loc[-6:] == '.parts': #manifests
        for l in manifest(r):
            yield l
    else: #normal download
        size = CHUNK_SIZE
        while size == CHUNK_SIZE:
            read = r.read(CHUNK_SIZE)
            size = len(read)
            yield read
        
def manifest(r):
    cache = {}
    l = r.readline()
    while l != b'':
        
        #get all URLs in this section
        urls = []
        while l != b'--\n':
            if l == b'':
                break
            l = l.decode('utf-8')
            l = l[:-1]
            urls.append(l)
            l = r.readline()
            
        #handle caching
        if '(*)' in urls:
            inCache = False
            
            #if a URL is in cache, yield its data
            for url in urls:
                if url in cache:
                    inCache = True
                    yield cache[url]
                    break
                
            #otherwise store the next valid download in cache
            if not inCache:
                for url in urls:
                    data = b''
                    try:
                        for x in download_file(url):
                            data = data + x
                            yield x
                        cache[url] = data
                        break
                    except: pass
                
        #when no caching is needed
        else:
            for url in urls:
                try:
                    for x in download_file(url):
                        yield x
                    break
                except: pass
        l = r.readline()
    

def files_from_sequence(stream):
    """
    Yield the files from the sequence in the order they are specified.

    stream: the return value (a generator) of a download_file
                        call that represents a file sequence
    """
    # Use next(stream) to yield the more data.
    array = bytearray()
    while True:
        while len(array) < 4:
            try:
                data = next(stream)
                array.extend(data)
            except: return
        numBytes = int.from_bytes(array[:4], 'big')
        array = array[4:]
        while len(array) < numBytes:
            try:
                data = next(stream)
                array.extend(data)
            except: 
                yield array
                return     
        yield array[:numBytes]
        array = array[numBytes:]
    

if __name__ == '__main__':
    """
    Remember you can use python3 gui.py URL_NAME to test your images!
    """
    pass