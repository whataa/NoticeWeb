import re

import requests
from bs4 import BeautifulSoup

from cdut.models import Article, Source, Type
from utils.util import stamp_format, date_to_time


class ABase:
    def __init__(self):
        self.aid = []
        self.aref = []

    def is_article_exists(url):
        if Article.objects.filter(origin_url=url):
            return True
        return False

class AIndexSpider(ABase):
    def __init__(self, url):
        self.__url = url
        self.__pattern = re.compile(r'news/(.{10})')

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
            print('Acdut has existed')
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

class AAaoSpider(ABase):
    def __init__(self, url):
        self.__url = url
        pass
    def start(self):
        rp = requests.get(self.__url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        for item in soup.find_all('img', alt='news'):
            subItem = item.find_next_sibling()
            id = self.__save(subItem)
            if not id:
                print('save faild')
                continue
            self.aid.append(id)
            self.aref.append(str(item.a['href']).strip())

    def __save(self,subItem):
        iurl = r'http://www.aao.cdut.edu.cn' + str(subItem['href']).strip()
        if self.is_article_exists(iurl):
            print('Aaao has existed')
            return None
        itime = date_to_time(str(subItem.span.string).strip().replace('(', '').replace(')', ''))
        ititle = str(subItem['title']).strip()
        artcle = Article(
            title=ititle,
            origin_url=iurl,
            addtime=itime,
            source=Source.objects.get(source_id=3),
            type=Type.objects.get(type_id=2),
        )
        artcle.save()
        return artcle.article_id