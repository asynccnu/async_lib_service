from aiohttp.web import Application, Response, json_response

from . import loop
from .database import db_setup
from .decorator import require_captcha, require_s, require_sid
from .paginate import _Pagination
from .spider import book_me, get_book, renew_book, search_books

api = Application()
attention = loop.run_until_complete(db_setup())

async def async_search_books(request):
    """
    :function: async_search_books
    :args: request
    :res: 图书信息
    :dec:搜索图书, 返回图书相关信息, 分页(每页20条)
    """
    pages = 20
    query_string = request.rel_url.query_string
    if query_string == None :
        return Response(body=b'{"args-error": "null"}',
                    content_type='application/json', status=401)

    keys = []
    values = []
    for item in query_string.split('&'):
        keys.append(item.split('=')[0])
        values.append(item.split('=')[1])
    args = dict(zip(keys, values))

    if "keyword" not in args:
        return json_response({
                "msg":"need keyword"
            })
    if "page" not in args:
        page = 1
    else:
        page = int(args['page'])
    keyword = args["keyword"]

    book_info_list = await search_books(keyword)
    page_info_list = _Pagination(book_info_list,page,pages)
    res = {
        'meta' : {
            'max' : page_info_list.max_page,
            'per_page' : 20
        },
        'result' :  book_info_list[(page-1)*pages:page*pages]
    }
    return json_response(res)


async def async_book_detail(request):
    """
    :function: async_book_detail
    :args: request
    :res: 图书详细信息
    图书详情
    """
    bid = request.match_info.get('id')
    book_detail = await get_book(bid)
    return json_response(book_detail)


@require_s
async def async_book_me(request,s):
    """
    :function: async_book_me
    :args: sid (cookie)
    """
    cookie = {'PHPSESSID' : s }
    res = await book_me(cookie)

    if res == 401:
        return Response(body = '[]',
                content_type='application/json', status=401)

    return json_response(res)


@require_captcha
@require_s
async def async_renew_book(request,s,captcha):
    """
    :function: async_renew_book
    :args:
        - request
        - s: 爬虫session对象
        - captcha: 验证码
    """
    cookie = {'PHPSESSID' : s }
    data = await request.json()
    bar_code = data['bar_code']
    check = data['check']
    res = await renew_book(cookie,captcha,bar_code,check)

    if res == 400 or res == 403 or res == 406:
        return Response(body = '{}',
                    content_type = 'application/json', status = res)

    return json_response(res)


@require_sid
async def async_create_attention(request,sid):
    """
    :function: async_create_atten
    :args:
        - request
        - sid: 学号
    :添加关注图书, 存储mongodb数据库
    """
    data = await request.json()
    book_bid = data['bid']
    book_name = data['book']
    book_id = data['book_id']
    book_author = data['author']
    att = {
        'bid' : book_bid,
        'book' : book_name,
        'id' : book_id,
        'author' : book_author,
        'sid' : sid
    }
    atten = await attention.attentiondb.find_one(att)
    if atten is not None :
        return Response(body=b'{"msg":"already attention"}',
                    content_type='application/json', status=401)

    atten = await attention.attentiondb.insert_one(att)
    att['_id'] = str(att['_id'])
    return json_response(att)


@require_sid
async def async_get_atten(request,sid):
    """
    :function: async_get_atten
    :args:
        - request
        - sid: 学号
    获取关注的图书列表
    """

    async def isavailable(book_id):
        """
        获取图书是否可借
        """
        book_list = await get_book(book_id)
        for book in book_list['books']:
            if book['status'].encode('utf-8') == b'\xe5\x8f\xaf\xe5\x80\x9f':
                return "y"
        return "n"

    all_book = []
    atten = attention.attentiondb.find({'sid':sid})
    tmp = []

    while True:
        if not atten.alive: break
        await atten.fetch_next
        one = atten.next_object()
        try:
            one['_id'] = str(one['_id'])
        except TypeError:
            return Response(body=b'{"msg": "no-attention"}',
                            content_type='application/json', status=404)
        tmp.append(one)

    for item in tmp:
        avbl = await isavailable(item['id'])
        all_book.append({
            'bid' : item['bid'],
            'book': item['book'],
            'id' : item['id'],
            'author': item['author'],
            'avb' : avbl
        })
    return json_response(all_book)


@require_sid
async def async_del_atten(request,sid):
    """
    :function: async_del_atten
    :args:
        - request
        - sid: 学号
    删除图书关注提醒
    """
    data = await request.json()
    book_id = data['id']
    deleted = await attention.attentiondb.delete_one({'sid':sid,'id':book_id})

    if deleted.deleted_count == 0:
        return Response(body=b'{"msg": "do-not-attention"}',
                    content_type='application/json', status=404)
    return Response(body=b'{"msg": "del success"}',
                content_type='application/json', status=200)


api.router.add_route('GET', '/search/',async_search_books, name='async_search_books')
api.router.add_route('GET', '/detail/{id}/',async_book_detail, name='async_book_detail')
api.router.add_route('GET', '/me/',async_book_me, name='async_book_me')
api.router.add_route('POST', '/renew/',async_renew_book, name='async_renew_book')
api.router.add_route('POST', '/create/',async_create_attention, name='async_create_attention')
api.router.add_route('GET', '/attention/',async_get_atten, name='async_get_attens')
api.router.add_route('DELETE', '/delete/',async_del_atten, name='async_del_atten')
