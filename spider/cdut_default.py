import requests
from bs4 import BeautifulSoup

from cdut.models import Notice


class DefaultSpider:
    def __init__(self, url):
        self.__url = url
    def getNotice(self):
        resp = requests.get(self.__url)
        resp.encoding = 'GBK'
        soup = BeautifulSoup(resp.content, 'html.parser')
        for item in soup.find_all('li'):
            Notice(title=item.a['title'], url=item.a['href'], time=str(item.span.string).strip('\n')).save()

