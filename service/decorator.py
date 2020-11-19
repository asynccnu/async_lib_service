import functools

from aiohttp.web import json_response


def require_s(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        s = req_headers.get("s")
        if not s:
            err_msg = "missing s: %s" % str(s)
            return json_response(data={"err_msg": err_msg}, status=401)
        return await f(request, s, *args, **kwargs)
    return decorator

def require_captcha(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        captcha = req_headers.get("captcha")
        if not captcha:
            err_msg = "missing captcha: %s" % str(captcha)
            return json_response(data={"err_msg": err_msg}, status=401)
        return await f(request, captcha, *args, **kwargs)
    return decorator


def require_sid(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        sid = req_headers.get("sid")
        if not sid:
            err_msg = "missing sid: %s" % str(sid)
            return json_response(data={"err_msg": err_msg}, status=401)
        return await f(request, sid, *args, **kwargs)
    return decorator
