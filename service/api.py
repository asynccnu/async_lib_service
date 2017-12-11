from .spider import search_books, get_book, book_me, renew_book
from .decorator import require_lib_login 
from aiohttp.web import Response, json_response, Application 
from .paginate import _Pagination
#from .db_model import connection, Attention

api = Application() 

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
    
    keys = []; values = []
    for item in query_string.split('&'):
        keys.append(item.split('=')[0])
        values.append(item.split('=')[1])
    args = dict(zip(keys, values))
    keyword = args['keyword'] 
    page = int(args['page']) or 1 
    book_info_list = await search_books(keyword) 
    page_info_list = _Pagination(book_info_list,page,pages)  
    res = {
        'max' : page_info_list.max_page, 
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
    query_string = request.rel_url.query_string 
    bid = query_string.split("=")[1] 
    book_detail = await get_book(bid) 
    return json_response(book_detail)

async def async_book_me(s): 
    """
    :function: async_book_me
    :args: s (cookie)
    """
    return json_response(book_me(s))



api.router.add_route('GET', '/search/',async_search_books, name='async_search_books')
api.router.add_route('GET', '/detail/',async_book_detail, name='async__book_detail')
api.router.add_route('GET', '/me/',async_book_me, name='async__book_me')