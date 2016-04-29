import re
import urllib.parse
import urllib.request

import requests
from bs4 import BeautifulSoup

from cdut.models import Article, Source, Type
from utils.util import stamp_format, date_to_time, str_to_time


class ABase:
    def __init__(self, url):
        self.url = url
        self.title = None
        self.origin_url = None
        self.author = None
        self.datetime = None
        # 文章列表
        self.cList = []

    @staticmethod
    def is_article_exists(url):
        if Article.objects.filter(origin_url=url):
            return True
        return False

    def start(self):
        pass


class AIndexSpider(ABase):
    def __init__(self, url):
        ABase.__init__(self, url)
        self.__pattern = re.compile(r'news/(.{10})')

    def start(self):
        rp = requests.get(self.url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all('li'):
            self.title = str(item.a['title']).strip()
            self.origin_url = str(item.a['href']).strip()
            self.author = ''
            self.datetime = stamp_format(re.findall(self.__pattern, str(item.a['href']))[0])
            self.cList.append(
                Article(
                    title=self.title,
                    origin_url=self.origin_url,
                    author=self.author,
                    addtime=self.datetime,
                    source=Source.objects.get(source_id=1),
                    type=Type.objects.get(type_id=1),
                )
            )
        return self


class AAjaxSpider(ABase):
    def __init__(self, url):
        ABase.__init__(self, url)
        self.pParam = re.compile(r'xwbh=\"(\d*)\"')
        self.pTitle = re.compile(r'xwbt=\"(.*)\";s')
        self.pTime = re.compile(r'fbsj=\"(.*)\"')
        self.ajaxRequestBody = {
            "callCount": "1",
            "page": "/xww/news2_mt.html",
            "httpSessionId": "975427C79D9B08A548341A01E174503A",
            "scriptSessionId": "A483A99F4F9BA40117A6D93A1C2D9EEE430",
            "c0-scriptName": "newsAjax",
            "c0-methodName": "getXwlist",
            "c0-id": "0",
            "c0-param0": "string:infoCont_140590539291880913_145802377061914235",
            "c0-param1": "Object_Object:{}",
            "c0-param2": "string:1000020114",
            "batchId": "0",
        }

    def start(self):
        result = self.__start_ajax_data(self.url, self.ajaxRequestBody)
        result = result.split('\n')
        result = result[3:-4]
        for item in result:
            tmpUrl = re.findall(self.pParam, str(item))[0]
            self.origin_url = 'http://www.cdut.edu.cn/xww/newPage.do?xwbh=' + tmpUrl + '&yyxwym=news'
            self.title = re.findall(self.pTitle, str(item))[0].encode('utf-8').decode('unicode_escape')
            self.datetime = str_to_time(re.findall(self.pTime, str(item))[0])
            self.cList.append(
                Article(
                    title=self.title,
                    origin_url=self.origin_url,
                    author='',
                    addtime=self.datetime,
                    source=Source.objects.get(source_id=1),
                    type=Type.objects.get(type_id=1),
                )
            )
        return self

    def __start_ajax_data(slef,url, data, referer=None, **headers):
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116')
        if referer:
            req.add_header('Referer', referer)
        if headers:
            for k in headers.keys():
                req.add_header(k, headers[k])
        params = urllib.parse.urlencode(data).encode(encoding='utf8')
        response = urllib.request.urlopen(req, params)
        result = response.read()
        return result.decode("utf8")


class AAaoSpider(ABase):
    def __init__(self, url):
        ABase.__init__(self, url)

    def start(self):
        rp = requests.get(self.url)
        soup = BeautifulSoup(rp.content, 'html.parser')

        for item in soup.find_all('img', alt='news'):
            subItem = item.find_next_sibling()
            self.title = str(subItem['title']).strip()
            self.origin_url = r'http://www.aao.cdut.edu.cn' + str(subItem['href']).strip()
            self.author = '教务处'
            self.datetime = date_to_time(str(subItem.span.string).strip().replace('(', '').replace(')', ''))
            self.cList.append(
                Article(
                    title=self.title,
                    origin_url=self.origin_url,
                    author=self.author,
                    addtime=self.datetime,
                    source=Source.objects.get(source_id=3),
                    type=Type.objects.get(type_id=2),
                )
            )
        return self


class ALibSpider(ABase):
    def __init__(self, url):
        ABase.__init__(self, url)

    def start(self):
        try:
            rp = requests.get(self.url,timeout=2)
        except:
            print('lib title timeout,break')
            return self
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all('li', class_='mainlist_li_notice'):
            self.title = str(item.a['title']).strip()
            self.origin_url = r'http://www.lib.cdut.edu.cn' + str(item.a['href']).strip()
            self.author = '图书馆'
            self.cList.append(
                Article(
                    title=self.title,
                    origin_url=self.origin_url,
                    author=self.author,
                    source=Source.objects.get(source_id=2),
                    type=Type.objects.get(type_id=2),
                )
            )
        return self


class AGraSpider(ABase):
    def __init__(self, url):
        ABase.__init__(self, url)

    def start(self):
        pattern = re.compile(r'</small>(.*) <small>')
        try:
            rp = requests.get(self.url,timeout=2)
        except:
            return self
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all(class_='title'):
            self.title = str(item.string).strip()
            self.origin_url = r'http://www.gra.cdut.edu.cn' + str(item['href']).strip()
            self.author = '研招办'
            self.datetime = str_to_time(re.search(pattern, str(item.find_next_sibling()))
                  .group().replace('</small>','').replace('<small>',''))
            self.cList.append(
                Article(
                    title=self.title,
                    origin_url=self.origin_url,
                    author=self.author,
                    addtime=self.datetime,
                    source=Source.objects.get(source_id=4),
                    type=Type.objects.get(type_id=3),
                )
            )
        return self


class ACistSpider(ABase):
    def __init__(self, url):
        ABase.__init__(self, url)

    def start(self):
        try:
            rp = requests.get(self.url)
        except:
            print('cist title timeout,break')
            return self
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all('span'):
            if item.a:
                continue
            if not item.find_next_sibling():
                continue
            sibItem = item.find_next_sibling()
            self.title = str(sibItem.string).strip()
            self.origin_url = r'http://www.cist.cdut.edu.cn' + str(sibItem['href']).strip()
            self.datetime = date_to_time(str(item.string).replace(' ', ''))
            self.cList.append(
                Article(
                    title=self.title,
                    origin_url=self.origin_url,
                    addtime=self.datetime,
                    source=Source.objects.get(source_id=5),
                    type=Type.objects.get(type_id=3),
                )
            )
        return self
