import json
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup

lib_login_test_url = "http://202.114.34.15/reader/redr_info.php"
lib_search_url = "http://202.114.34.15/opac/openlink.php"
lib_me_url = "http://202.114.34.15/reader/book_lst.php"
lib_detail_url = "http://202.114.34.15/opac/item.php?marc_no=%s"
lib_renew_url = "http://202.114.34.15/reader/ajax_renew.php"
douban_url = "https://api.douban.com/v2/book/isbn/%s"

async def search_books(keyword):
    search_url = lib_search_url
    headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    }

    post_data = {
       'strSearchType': 'title', 
        'match_flag': 'forward',
	'historyCount': '1',
        'strText': keyword,
        'doctype': 'ALL',
	'displaypg': '100',
        'showmode': 'list', 
        'sort': 'CATA_DATE',
	'orderby': 'desc',
        'dept': 'ALL' 
    }
    async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True), headers = headers) as session:
        async with session.post(search_url, data = post_data, headers = headers) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html5lib')
            book_list_info = soup.find_all('li', class_ = 'book_list_info')
            book_info_list = []
            #因为图书简介变成了Ajax动态获取，如果要获取图书简介就需要一个一个页面进去
            #取得isbn, 之后再一次次请求豆瓣API, 这样耗时了，所以不如直接返回学校
            #学校图书馆的url, 让用户自己去访问
            for book_info in book_list_info:
                if book_info:
                    book = book_info.find('a', href=re.compile('item.php*')).string
                    marc_no_link = book_info.find('a').get('href')
                    marc_no = marc_no_link.split('=')[-1]
                    book_info_list.append({
                        'book' : book,
                        'author' : ' '.join(book_info.p.text.split()[2:-4]),
                        'publisher': book_info.p.text.split()[-4],
                        'bid' : 'fff',
                        'bookurl': 'http://202.114.34.15/opac/' + marc_no_link,
                        'id' : marc_no,
                    })
            print('------------------')
            print(book_info_list)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_books("骆驼祥子"))
    loop.close()
