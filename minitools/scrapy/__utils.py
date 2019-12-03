import chardet

__all__ = "refresh_encoding",


# guess the most suitable coding for response by chardet
def refresh_encoding(response, body=None, encoding=None):
    response._cached_ubody = None
    if body:
        response._body = body
    response._encoding = encoding or chardet.detect(response.body)['encoding']
    return response
