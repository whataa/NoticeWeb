import json
import re

import requests
from bs4 import BeautifulSoup

from cdut.models import Content, File, Article
from utils.util import stamp_format, str_to_time


class CIndexSpider:
    def __init__(self, url, aid):
        self.__url = url
        self.__aid = aid
        self.__pt = re.compile(r'：(.*)')
        self.__content = []
        self.file_url = None
        self.file_name = None
        self.file_type = None


    def start(self):
        rp = requests.get(self.__url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        # 发布者
        self.__author = re.findall(self.__pt, str(soup.find('span', class_='puber').text).replace('\n', ''))[0]
        # 发布时间
        self.__datetime = re.findall(self.__pt, str(soup.find('span', class_='pubtime').text).replace('\n', ''))[0]
        content = soup.find('div', id='contentdisplay')
        for p in soup.find_all('p', class_='MsoNormal'):
            # 图片链接
            if p.img:
                self.__content.append({'img': p.img['src']})
            # 是否有内容标签
            elif p.span:
                # 标签里没有内容
                if not p.span.text:
                    continue
                if str(p.text).strip().startswith('附件：') or str(p.text).strip().startswith('下载：'):
                    if p.a:
                        self.file_url = p.a['href']
                        self.file_name = str(p.text).strip().replace('\n', '').replace('附件：', '').replace('下载：', '')
                        self.file_type = self.file_url.split('.')[-1]
                    continue
                if p.a:
                    self.__content.append({'href': p.a['href']})
                    continue
                if not str(p.text).strip():
                    continue
                if p.has_attr('align'):
                    self.__content.append({'content': str(p.text).strip().replace('\n', ''), 'align': p['align']})
                    continue
                self.__content.append(
                    {'content': str(p.text).strip().replace('\n', '')})
        self.__content = json.dumps(self.__content, ensure_ascii=False)

        content_id = self.__save(self.__aid)
        if content_id and self.file_url:
            self.__savefile(content_id)

    def __save(self, aid):
        if Content.objects.filter(article=self.__aid):
            print('content has existed')
            return None
        content = Content(
            article=Article.objects.get(article_id=self.__aid),
            content=self.__content,
            datetime=str_to_time(self.__datetime)
        )
        content.save()
        return content.content_id

    def __savefile(self, cid):
        File(
            content=Content.objects.get(content_id=cid),
            url=self.file_url,
            name=self.file_name,
            type=self.file_type
        ).save()
