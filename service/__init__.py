import json
import functools
import aiohttp
from aiohttp.web import Response

lib_test_url = ''

def require_lib_login(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        PHPSESSID = req_headers['PHPSESSID']
        if PHPSESSID:
            cookies = { 'PHPSESSID' : PHPSESSID }
            return await f(request, cookies, None, *args, **kwargs)
        else:
            return Response(
                body = b'',
                content_type = 'application/json',
                status = 401
            )
