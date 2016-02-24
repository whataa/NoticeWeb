import re

import datetime
import requests
from bs4 import BeautifulSoup

from cdut.models import Article, Source, Type


class DefaultSpider:
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
        if Article.objects.filter(origin_url=str(item.a['href']).strip()):
            print('has existed')
            return None
        itime = datetime.datetime.fromtimestamp(
            int(re.findall(self.__pattern, str(item.a['href']))[0])
        ).strftime('%Y-%m-%d %H:%M:%S')
        artcle = Article(
            title=str(item.a['title']).strip(),
            origin_url=str(item.a['href']).strip(),
            addtime=itime,
            source=Source.objects.get(source_id=1),
            type=Type.objects.get(type_id=1),
        )
        artcle.save()
        return artcle.article_id
