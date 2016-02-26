import re

import requests
from bs4 import BeautifulSoup

from cdut.models import Article, Source, Type
from utils.util import stamp_format

class ABaseSpider:
    def is_article_exists(url):
        if Article.objects.filter(origin_url=url):
            return True
        return False

class AIndexSpider(ABaseSpider):
    def __init__(self, url):
        self.__url = url
        self.__pattern = re.compile(r'news/(.{10})')
        self.aid = []
        self.aref = []

    def start(self):
        rp = requests.get(self.__url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all('li'):
            id = self.__save(item)
            if not id:
                print('save faild')
                continue
            self.aid.append(id)
            self.aref.append(str(item.a['href']).strip())

    def __save(self, item):
        if self.is_article_exists(str(item.a['href']).strip()):
            print('has existed')
            return None
        itime = stamp_format(re.findall(self.__pattern, str(item.a['href']))[0])
        artcle = Article(
            title=str(item.a['title']).strip(),
            origin_url=str(item.a['href']).strip(),
            addtime=itime,
            source=Source.objects.get(source_id=1),
            type=Type.objects.get(type_id=1),
        )
        artcle.save()
        return artcle.article_id

class AAaoSpider(ABaseSpider):
    def __init__(self, url):
        self.__url = url
        pass
    def start(self):
        rp = requests.get(self.__url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all('img', alt='news'):
            subItem = item.find_next_sibling()
            print('href =', r'http://www.aao.cdut.edu.cn' + str(subItem['href']).strip())
            print('title =', str(subItem['title']).strip())
            print('time =', str(subItem.span.string).strip().replace('(', '').replace(')', ''))
        pass
    def __save(self,subItem):
        if self.is_article_exists(r'http://www.aao.cdut.edu.cn' + str(subItem['href']).strip()):
            pass