import chardet

from w3lib.encoding import http_content_type_encoding

__all__ = "refresh_response", "guess_coding",


# guess the most suitable coding for response by chardet
def refresh_response(response, body=None, encoding=None):
    response._cached_ubody = None
    if body:
        response._body = body
    response._encoding = encoding or chardet.detect(response.body)['encoding']
    return response


# guess the most suitable coding for body by chardet and w3lib
def guess_coding(body):
    return http_content_type_encoding(f'charset={chardet.detect(body)["encoding"]}')
