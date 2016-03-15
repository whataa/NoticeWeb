import re

import requests
from bs4 import BeautifulSoup

from cdut.models import Article, Source, Type
from utils.util import stamp_format, date_to_time


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
            self.author = ''
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
