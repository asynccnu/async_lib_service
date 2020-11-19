import asyncio
import datetime
import re
import time
from pprint import pprint

import aiohttp
from bs4 import BeautifulSoup

lib_login_test_url = "http://202.114.34.15/reader/redr_info.php"
lib_search_url = "http://202.114.34.15/opac/openlink.php"
lib_me_url = "http://202.114.34.15/reader/book_lst.php"
lib_detail_url = "http://202.114.34.15/opac/item.php?marc_no=%s"
lib_renew_url = "http://202.114.34.15/reader/ajax_renew.php"
douban_url = "https://api.douban.com/v2/book/isbn/%s"

cookie = {'PHPSESSID' : 'ST-116-DcGgZOHMt7gVIuKvxMeA-accountccnueducn' }
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
}

#'bar_code': 'T112009478', 'check': 'F0780D4E',

async def test():
    #print('\r\n\r\n' + "[TEST]Start test SearchBooks..." + '\r\n\r\n')
    #data = await search_books("亲爱的三毛")
    #print(data)

    #print('\r\n\r\n' + "[TEST]Start test BookMe..." + '\r\n\r\n')
    #data = await book_me(cookie)
    #print(data)

    #print('\r\n\r\n' + "[TEST]Start test ReNew..." + '\r\n\r\n')
    #data = await renew_book(cookie, 'ZZEP', 'T112009478', 'F0780D4E')
    #print(data)

    print('\r\n\r\n' + "[TEST]Start test GetInof..." + '\r\n\r\n')
    data = await get_book('0001419574')
    pprint(data)

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
                    marc_no = '0'
                    match_obejct = re.match('.*marc_no=(.*)&list.*', marc_no_link)
                    if match_obejct is not None:
                        marc_no = match_obejct.group(1)

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

            # 跳转到统一认证服务，401
            if "统一身份认证服务" in str(html):
                return 401
            # 该记录为空，直接返回，不然下面会有out index 错误
            elif "您的该项记录为空" in str(html):
                return []

            soup = BeautifulSoup(html, 'lxml')
            bids = []
            a_tags = soup.find_all('a', class_ = 'blue')
            for a_tag in a_tags:
                bids.append(a_tag.get('href').split("=")[-1])
            _my_book_list = soup.find_all('tr')[1:]
            my_book_list = []
            #最后两个是垃圾信息，一个是二维码一个是无用信息

            # 去除最后两个
            _my_book_list = _my_book_list[0:len(_my_book_list)-2]

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
            try :
                res_color = BeautifulSoup(html, 'lxml').find('font')['color']
            except TypeError :                                      # 验证码错误，返回是一句话"验证码错误"，无法解析
                return 400
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
            if len(alldd) == 2:
                return {
                    'bid':'',
                    'book':'',
                    'author':'',
                    'intro':'',
                    'books':[]
                }
            book = alldd[0].text.split("/")[0]
            #有可能没有作者
            try:
                author = alldd[0].text.split("/")[1]
            except:
                author = ''

            #获取豆瓣简介
            isbn = alldd[2].text.split("/")[0]
            douban = douban_url % isbn
            async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe = True),headers = headers) as dsession:
                async with dsession.get(douban) as dresp:
                    rd = await dresp.json()
                    intro = rd.get("summary")
            if intro == None:
                intro = ""

            #Booklist
            booklist = []
            _booklist = soup.find(id = 'tab_item').find_all('tr', class_ = 'whitetext')

            #可能没有馆藏图书
            if "此书刊可能正在订购中或者处理中" in str(_booklist[0]):
                bid = _booklist[0].td.text
            else:
                for _book in _booklist:
                    bid = _book.td.text
                    tid = _book.td.next_sibling.next_sibling.string
                    lit = _book.text.split()
                    #状态共有 可借 无法借阅 保留本 已还 借出
                    try:
                        if lit[-1] == "可借" or lit[-2] == "可借":
                            status = "可借"
                            date = ""
                            if lit[-1] == "可借":
                                room = lit[-2]
                            elif lit[-2] == "可借":
                                room = lit[-3]
                        elif lit[-2] == "正常验收" or lit[-2]=="在编" or lit[-1] == "阅览" or lit[-1] == "剔旧报废" or lit[-1] == "非可借":
                            status = "无法借阅"
                            date = ""
                            if lit[-2] == "正常验收" or lit[-2]=="在编":
                                room = lit[-1]
                            elif lit[-1] == "阅览" or lit[-1] == "剔旧报废" or lit[-1] == "非可借":
                                room = lit[3]
                        elif lit[-1] == "保留本":
                            status = lit[-1]
                            date = ""
                            room = lit[-2]
                        elif "已还" in lit[4] and "正在上架" in lit[4]:
                            status = "已还"
                            date = ""
                            room = lit[3]
                        elif "借出" in lit[-2] and "应还日期" in lit[-2]:
                            status = "借出"
                            datestart = lit[-2].find("：") + 1
                            date = lit[-2][datestart:]
                            room = lit[2]
                        elif '-' in lit[-1]:
                            date = lit[-1][-10:]
                            status = lit[-1][:2]
                            room = lit[-2]
                        else:
                            status = lit[-1]
                            room = lit[-2]
                            tid = tid
                            date = ""
                    except:
                        status = lit[-1]
                        room = lit[-2]
                        tid = tid
                        date = ""

                    booklist.append({
                        "status":status,
                        "room":room,
                        "bid":bid,
                        "tid":tid,
                        "date":date,
                    })

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
