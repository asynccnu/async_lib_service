import json
import re
import asyncio
import aiohttp
import time
import datetime
from bs4 import BeautifulSoup

lib_login_test_url = "http://202.114.34.15/reader/redr_info.php"
lib_search_url = "http://202.114.34.15/opac/openlink.php"
lib_me_url = "http://202.114.34.15/reader/book_lst.php"
lib_detail_url = "http://202.114.34.15/opac/item.php?marc_no=%s"
lib_renew_url = "http://202.114.34.15/reader/ajax_renew.php"
douban_url = "https://api.douban.com/v2/book/isbn/%s"

cookie = {'PHPSESSID' : 'ST-1562-eqRFWH0fyzOkvKdSsXZ9-accountccnueducn'}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
}

#'bar_code': 'T112009478', 'check': 'F0780D4E', 

async def test():
    print('\r\n\r\n' + "[TEST]Start test SearchBooks..." + '\r\n\r\n')
    await search_books("亲爱的三毛")
    print('\r\n\r\n' + "[TEST]Start test BookMe..." + '\r\n\r\n')
    await book_me(cookie)
    print('\r\n\r\n' + "[TEST]Start test ReNew..." + '\r\n\r\n')
    await renew_book(cookie, 'XXSK', 'T112009478', 'F0780D4E')

async def search_books(keyword):
    search_url = lib_search_url
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
        async with session.post(search_url, data = post_data) as resp:
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
            print(book_info_list)

async def book_me(s):
    """
    :function: 图书借阅记录
    :s: cookie
    """
    me_url = lib_me_url
    async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True), cookies = s, headers = headers) as session:
        async with session.get(me_url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html5lib')
            bids = []
            a_tags = soup.find_all('a', class_ = 'blue')
            for a_tag in a_tags:
                bids.append(a_tag.get('href').split("=")[-1])
            _my_book_list = soup.find_all('tr')[1:]
            my_book_list = []
            #最后两个是垃圾信息，一个是二维码一个是无用信息
            _my_book_list = _my_book_list[0:2]
            for index, _book in enumerate(_my_book_list):
                text = _book.text.split('\n')
                itime = text[3][5:]; otime = text[4][5:15]
                date_itime = datetime.datetime.strptime(itime, "%Y-%m-%d")
                date_otime = datetime.datetime.strptime(otime, "%Y-%m-%d")
                ctime = datetime.datetime.now().strftime("%Y-%m-%d")
                dtime = time.mktime(date_otime.timetuple()) - \
                    time.mktime(datetime.datetime.now().timetuple())

                renew_button = _book.find('input')['onclick']
                renew_info = [eval(i) for i in renew_button[renew_button.index('(')+1:\
                                   renew_button.index(')')].split(',')]
                bar_code = renew_info[0]
                check = renew_info[1]

                my_book_list.append({
                    'book': text[2].split('/')[0].strip(),
                    'author': text[2].split('/')[-1].strip(),
                    'itime': str(itime),
                    "otime": str(otime),
                    "time": int(dtime/(24*60*60)),
                    "room": text[6].strip(),
                    "bar_code": bar_code,
                    "check": check,
                    "id": bids[index]
                        })
        for i in my_book_list:
            print('----------')
            print(i)
            print('----------')

async def renew_book(s, captcha, bar_code, check):
    renew_url = lib_renew_url
    now = int(time.time()*1000)
    payload = {
        'bar_code': bar_code,
        'check': check,
        'time': now,
        'captcha': captcha
    }
    async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True),
            cookies = s, headers = headers) as session:
        async with session.post(renew_url, data = payload) as resp:
            html = await resp.text()
            res_color = BeautifulSoup(html, "html5lib").find('font')['color']
            if res_color == 'green':
                res_code = 200
            else:
                res_string = BeautifulSoup(html, "html5lib").find('font').string.strip()
                early = '不到续借时间，不得续借！'
                unavailable = '超过最大续借次数，不得续借！'
                if res_string == early:
                    res_code = 406
                elif res_string == unavailable:
                    res_code = 403
                else:
                    res_code = 400
            print(res_string + '-> ' + str(res_code))
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
