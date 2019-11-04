from minitools import next_page

__all__ = ('next_page_request',)


def next_page_request(response, rule, **kwargs):
    request = response.request
    method = request.method
    if method == 'GET':
        return request.replace(url=next_page(response.url, rule, **kwargs))
    elif method == 'POST':
        return request.replace(
            body=next_page(response.body.decode(), rule, **kwargs).encode(),
            dont_filter=True)
    else:
        raise Exception('This Func just Support `GET`/`POST`!')
