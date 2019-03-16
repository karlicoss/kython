import requests # type: ignore


def is_alive(url: str) -> bool:
    res = requests.head(
        url,
        allow_redirects=True,
        headers={
            'User-Agent': 'kython',
        },
    )
    st = res.status_code
    if st in (429,):
        raise RuntimeError(str(res))
    if st in (200,):
        return True
    # TODO not sure, might need to check status manually
    # TODO e.g. too many requests should be more of an exception...
    # return res.ok
    raise AssertionError(f'unhandled status {res}')
