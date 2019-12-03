import chardet

__all__ = "refresh_encoding",


# guess the most suitable coding for response by chardet
def refresh_encoding(response, encoding=None):
    response._cached_ubody = None
    response._encoding = encoding or chardet.detect(response.body)['encoding']
    return response
