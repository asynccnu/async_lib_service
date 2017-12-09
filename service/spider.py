import json
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
            print(await resp.text())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_books("骆驼祥子"))
    loop.close()
