import json
import re

import requests
from bs4 import BeautifulSoup

from cdut.models import Content, File, Article
from utils.util import str_to_time, get_filetype


class CBase:
    def __init__(self, url, aid):
        self.url = url    #文章URL
        self.aid = aid    #对应的Article的ID
        self.content = [] #内容
        self.author = None
        self.datetime = None  #发布时间
        self.file_url = None    #附件URL
        self.file_name = None   #附件名
        self.file_type = None   #附件类型

    @staticmethod
    def is_content_exists(aid):
        if Content.objects.filter(article=aid):
            return True
        return False

    #保存内容
    def save(self, aid):
        if Content.objects.filter(article=aid):
            print('content has existed')
            return None
        content = Content(
            article=Article.objects.get(article_id=self.aid),
            content=self.content,
            datetime=self.datetime
        )
        content.save()
        if self.author:
            self.updateArticle()
        return content.content_id

    #保存附件
    def savefile(self, cid):
        File(
            content=Content.objects.get(content_id=cid),
            url=self.file_url,
            name=self.file_name,
            type=self.file_type
        ).save()

    def updateArticle(self):
        article=Article.objects.get(article_id=self.aid)
        article.author = self.author
        article.save()

class CIndexSpider(CBase):
    def __init__(self, url, aid):
        CBase.__init__(self,url,aid)
        self.__pt = re.compile(r'：(.*)')

    def start(self):
        if CBase.is_content_exists(self.aid):#!!!!!!!!!!浪费一晚上，参数传错为url！！！
            print('content exists')
            return
        rp = requests.get(self.url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        # 发布者
        self.author = re.findall(self.__pt, str(soup.find('span', class_='puber').text).replace('\n', ''))[0]
        # 发布时间
        self.datetime = str_to_time(re.findall(self.__pt, str(soup.find('span', class_='pubtime').text).replace('\n', ''))[0])
        content = soup.find('div', id='contentdisplay')
        for p in soup.find_all('p', class_='MsoNormal'):
            # 图片链接
            if p.img:
                self.content.append({'img': p.img['src']})
            # 是否有内容标签
            elif p.span:
                # 标签里没有内容
                if not p.span.text:
                    continue
                if str(p.text).strip().startswith('附件：') or str(p.text).strip().startswith('下载：'):
                    if p.a:
                        self.file_url = p.a['href']
                        self.file_name = str(p.text).strip().replace('\n', '').replace('附件：', '').replace('下载：', '')
                        self.file_type = get_filetype(self.file_url)
                    continue
                if p.a:
                    self.content.append({'href': p.a['href']})
                    continue
                if not str(p.text).strip():
                    continue
                if p.has_attr('align'):
                    self.content.append({'content': str(p.text).strip().replace('\n', ''), 'align': p['align']})
                    continue
                self.content.append(
                    {'content': str(p.text).strip().replace('\n', '')})
        self.content = json.dumps(self.content, ensure_ascii=False)

        content_id = self.save(self.aid)
        if content_id and self.file_url:
            self.savefile(content_id)



class CAaoSpider(CBase):
    def __init__(self,url,aid):
        CBase.__init__(self,url,aid)
        self.__pt = re.compile(r'/> (.*) <a')

    def start(self):
        if CBase.is_content_exists(self.aid):#!!!!!!!!!!浪费一晚上，参数传错为url！！！
            print('content exists')
            return
        rp = requests.get(self.url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        #内容
        content = soup.find('div', id='text')
        for p in content.p.find_all('p'):
            if not p.text:
                continue
            if not str(p.text).strip():
                continue
            if p.has_attr('text-align'):
                self.content.append({'content':str(p.text).strip().replace('\n',''), 'align':p['text-align']})
                continue
            self.content.append({'content':str(p.text).strip().replace('\n','')})
        #表格
        if content.p.find('table'):
            self.content.append({'table':str(content.p.table)})
        #附件
        if content.p.find('a'):
            self.file_name = re.findall(self.__pt, str(content.p))[0]
            #移除链接前的.符号
            self.file_url = r'http://www.aao.cdut.edu.cn/aao' + content.p.a['href'][1:]
            self.file_type = get_filetype(self.file_url)
        self.author = '教务处'

        self.content = json.dumps(self.content, ensure_ascii=False)

        content_id = self.save(self.aid)
        if content_id and self.file_url:
            self.savefile(content_id)




















