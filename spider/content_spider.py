import json
import re

import requests
from bs4 import BeautifulSoup

from cdut.models import Content, File, Article
from utils.util import str_to_time, get_filetype


class CBase:
    def __init__(self, url):
        self.url = url  # 文章URL
        self.content = []  # 内容
        self.author = None
        self.datetime = None  # 发布时间
        self.file_url = None  # 附件URL
        self.file_name = None  # 附件名
        self.file_type = None  # 附件类型

    @staticmethod
    def is_content_exists(aid):
        try:
            if Content.objects.get(article=aid):
                return True
        except:
            print('is_content_exists: false',aid)
            return False

    # 保存内容
    def save(self, aid):
        print('start save content: ' + self.url,aid)
        # 抓取失败，跳过保存
        if  (not self.content) and (not self.datetime):
            print('content not save,break')
            return None
        try:
            Content.objects.get(article=aid)
            print('content has existed')
            return None
        except Content.DoesNotExist:
            print('content not existed, exception')
            if self.datetime:
                content = Content(
                    article=Article.objects.get(article_id=aid),
                    content=self.content,
                    datetime=self.datetime,
                )
            else:
                content = Content(
                    article=Article.objects.get(article_id=aid),
                    content=self.content,
                )
            content.save()
            print('save content')
            if self.author:
                self.updateArticle(aid)
                print('updateArticle')
            return content.content_id

    # 保存附件
    def savefile(self, cid):
        File(
            content=Content.objects.get(content_id=cid),
            url=self.file_url,
            name=self.file_name,
            type=self.file_type
        ).save()
        print('savefile')

    def updateArticle(self, aid):
        article = Article.objects.get(article_id=aid)
        article.author = self.author
        article.save()


class CIndexSpider(CBase):
    def __init__(self, url):
        CBase.__init__(self, url)
        self.__pt = re.compile(r'：(.*)')

    def start(self):
        rp = requests.get(self.url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        # 发布者
        self.author = re.findall(self.__pt, str(soup.find('span', class_='puber').text).replace('\n', ''))[0]
        # 发布时间
        self.datetime = str_to_time(
            re.findall(self.__pt, str(soup.find('span', class_='pubtime').text).replace('\n', ''))[0])
        content = soup.find('div', id='contentdisplay')
        MsoNormal = content.find_all('p', class_='MsoNormal')
        Default = content.find_all('p', class_='Default')
        if (len(MsoNormal)-len(Default))>0:
            findResult = MsoNormal
        else:
            findResult = Default
        for p in findResult:
            # 图片链接
            if p.img and p.img.has_attr('src'):
                self.content.append({'img': p.img['src']})
            # 是否有内容标签
            elif p.span:
                # 标签里没有内容
                if not p.span.text:
                    continue
                if str(p.text).strip().startswith('附件：') or str(p.text).strip().startswith('下载：'):
                    if p.a and p.a.has_attr('href'):
                        self.file_url = p.a['href']
                        self.file_name = str(p.text).strip().replace('\n', '').replace('附件：', '').replace('下载：', '')
                        self.file_type = get_filetype(self.file_url)
                    continue
                if p.a and p.a.has_attr('href'):
                    tmpFile = p.find_all('a', class_='ke-insertfile')
                    if tmpFile:
                        self.file_name = p.a.text
                        self.file_url = p.a['href']
                        self.file_type = get_filetype(self.file_url)
                    else:
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

        return self


class CAaoSpider(CBase):
    def __init__(self, url):
        CBase.__init__(self, url)
        self.__pt = re.compile(r'/> (.*) <a')

    def start(self):
        rp = requests.get(self.url)
        soup = BeautifulSoup(rp.content, 'html.parser')
        self.datetime = None
        # 内容
        content = soup.find('div', id='text')
        for p in content.p.find_all('p'):
            if not p.text:
                continue
            if not str(p.text).strip():
                continue
            if p.has_attr('text-align'):
                self.content.append({'content': str(p.text).strip().replace('\n', ''), 'align': p['text-align']})
                continue
            self.content.append({'content': str(p.text).strip().replace('\n', '')})
        # 表格
        if content.p.find('table'):
            self.content.append({'table': str(content.p.table)})
        # 附件
        tmp = content.p.find('a')
        if tmp and tmp.find_previous_sibling() \
                and tmp.find_previous_sibling().name=='img':
            print('contnet has file: '+self.url)
            self.file_name = re.findall(self.__pt, str(content.p))[0]
            # 移除链接前的.符号
            self.file_url = r'http://www.aao.cdut.edu.cn/aao' + content.p.a['href'][1:]
            self.file_type = get_filetype(self.file_url)
        self.content = json.dumps(self.content, ensure_ascii=False)
        return self

class CLibSpider(CBase):
    def __init__(self, url):
        CBase.__init__(self, url)

    def start(self):
        try:
            rp = requests.get(self.url,timeout=2)
            rp.encoding='GB2312'
        except:
            print('libContent connect timeout,break')
            return self
        soup = BeautifulSoup(rp.text, 'html.parser')
        #内容
        content = soup.find('div', id='passage')
        first_tr = content.table.find('tr')
        for next in first_tr.find_next_siblings():
            #删除分享
            if next.find(class_='bshare-custom'):
                del next
                continue
            for item in next.td.p:
                if str(item).startswith('<div'):
                    if item.table:
                        self.content.append({'table': str(item.table)})
                    else:
                        if not item.text.strip()=='':
                            if item.has_attr('align'):
                                self.content.append({'content': item.text.strip(), 'align': item['align']})
                            else:
                                self.content.append({'content': item.text.strip()})
                elif str(item).startswith('<p'):
                    if (not item.img) and (not item.div) and (not item.table):
                        if item.text:
                            self.content.append({'content': item.text})
                    elif item.img and item.img.has_attr('src'):
                        self.content.append({'img': item.img['src']})
                    else:
                        for subitem in item:
                            if str(subitem).startswith('<div'):
                                if not subitem.text.strip()=='':
                                    if subitem.has_attr('align'):
                                        self.content.append({'content': subitem.text.strip(), 'align': subitem['align']})
                                    else:
                                        self.content.append({'content': subitem.text.strip()})
                            elif str(subitem).startswith('<table'):
                                self.content.append({'table': str(subitem)})
            self.content = json.dumps(self.content, ensure_ascii=False)
            return self


class CCistSpider(CBase):
    def __init__(self, url):
        CBase.__init__(self, url)

    def start(self):
        try:
            rp = requests.get(self.url,timeout=2)
            rp.encoding='utf8'
        except:
            print('cistContent connect timeout,break')
            return self
        soup = BeautifulSoup(rp.content, 'html.parser')
        info = soup.find('div',class_='info')
        pattern = re.compile(r'>作者:</small>(.*)<small>')
        author = re.findall(pattern,str(info))
        if author:
            self.author = author[0]
        content = soup.find('div', class_='content')
        for p in content.table.tr.td:
            if not str(p).strip():
                continue
            if str(p).startswith('<div'):
                self.content.append({'content': str(p.text).strip()})
                if p.p and p.p.img and p.p.img.has_attr('src'):
                    self.content.append({'img': r'http://www.cist.cdut.edu.cn' + p.p.img['src']})
            elif str(p).startswith('<p'):
                if not p.text:
                    continue
                if not str(p.text).strip():
                    continue
                self.parsecontent(p)
            elif str(p).startswith('<span'):
                if not p.p:
                    continue
                for subp in p:
                    if not subp.text:
                        continue
                    if not str(subp.text).strip():
                        continue
                    self.parsecontent(subp)
            elif str(p).startswith('<table'):
                self.content.append({'table': p})
        self.content = json.dumps(self.content, ensure_ascii=False)
        return self

    def parsecontent(self,p):
        if p.img:
            if p.a:
                self.file_name = p.a.text
                self.file_url = r'http://www.cist.cdut.edu.cn' + p.a['href']
                self.file_type = get_filetype(self.file_url)
            elif p.img.has_attr('src'):
                self.content.append({'img': r'http://www.cist.cdut.edu.cn' + p.img['src']})
        else:
            if p.has_attr('style') and ('text-align:right' in p['style']):
                self.content.append({'content': str(p.text).strip(), 'align': 'right'})
            else:
                self.content.append({'content': str(p.text).strip()})


class CGraSpider(CBase):
    def __init__(self, url):
        CBase.__init__(self, url)

    def start(self):
        pass
