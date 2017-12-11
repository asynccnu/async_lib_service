import json
import re
import lxml
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

cookie = {'PHPSESSID' : 'l4edbfgkgq3dgb80dr6ll5pmr6' }
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
    await renew_book(cookie, 'ZEPW', 'T112009478', 'F0780D4E')
    print('\r\n\r\n' + "[TEST]Start test GetInof..." + '\r\n\r\n')
    await get_book('0001477335')

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
            soup = BeautifulSoup(html, 'lxml')
            book_list_info = soup.find_all('li', class_ = 'book_list_info')
            book_info_list = []
            #因为图书简介变成了Ajax动态获取，如果要获取图书简介就需要一个一个页面进去
            #取得isbn, 之后再一次次请求豆瓣API, 这样在搜索结果多的时候会十分耗时，
            #所以不如直接返回学校图书馆的url, 让用户自己去访问
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
            return book_info_list

async def book_me(s):
    """
    :function: 图书借阅记录
    :s: cookie
    """
    me_url = lib_me_url
    async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True), cookies = s, headers = headers) as session:
        async with session.get(me_url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'lxml')
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
                itime = text[3][:].strip(); otime = text[4][:15].strip()
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
        print("in the book_me")
        print(my_book_list)
        for i in my_book_list:
            print(i)
            print('.')
        return my_book_list 

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
            res_color = BeautifulSoup(html, 'lxml').find('font')['color']
            if res_color == 'green':
                res_code = 200
            else:
                res_string = BeautifulSoup(html, 'lxml').find('font').string.strip()
                early = '不到续借时间，不得续借！'
                unavailable = '超过最大续借次数，不得续借！'
                if res_string == early:
                    res_code = 406
                elif res_string == unavailable:
                    res_code = 403
                else:
                    res_code = 400
            print(res_string + '-> ' + str(res_code))
            return res_code

async def get_book(id):
    detail_url = lib_detail_url % id
    async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True),
                headers = headers) as session:
        async with session.get(detail_url) as resp:
            thehtml = await resp.text()
            soup = BeautifulSoup(thehtml, 'lxml')
            alldd = soup.find_all('dd')
            book = alldd[0].text.split("/")[0]
            author = alldd[0].text.split("/")[1]
            
            #获取豆瓣简介
            isbn = alldd[2].text.split("/")[0]
            douban = douban_url % isbn
            async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True),headers = headers) as dsession:
                async with dsession.get(douban) as dresp:
                    rd = await dresp.json()
                    intro = rd.get("summary")
            
            #Booklist
            booklist = []
            _booklist = soup.find(id = 'tab_item').find_all('tr', class_ = 'whitetext')
            for _book in _booklist:
                bid = _book.td.text
                tid = _book.td.next_sibling.next_sibling.string
                lit = _book.text.split()
                if '-' in lit[-1]:
                    date = lit[-1][-10:]
                    status = lit[-1][:2]
                    booklist.append({
                        "status": status, "room": lit[-2], "bid": bid,
                        "tid": tid, "date": date })
                else:
                    booklist.append({"status": lit[-1], "room": lit[-2], "tid": tid})
            #return({'bid', 'book', 'author' ...})
            return ({
                    'bid':bid, 
                    'book':book,
                    'author':author,
                    'intro':intro,
                    'books':booklist
                 })

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
