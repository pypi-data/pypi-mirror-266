

def is_localhost(url):
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    # Check if the hostname is localhost or 127.0.0.1
    return parsed_url.hostname in ('localhost', '127.0.0.1')