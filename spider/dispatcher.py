import re

from spider.article_spider import AIndexSpider, AAaoSpider, AAjaxSpider, ALibSpider, ACistSpider
from spider.content_spider import CIndexSpider, CAaoSpider, CLibSpider, CCistSpider


def index(url):
    return AIndexSpider(url).start()
def ajax(url):
    return AAjaxSpider(url).start()
def indexContent(url):
    return CIndexSpider(url).start()
    pass

def aao(url):
    return AAaoSpider(url).start()
def aaoContent(url):
    return CAaoSpider(url).start()
    pass

def lib(url):
    return ALibSpider(url).start()
def libContent(url):
    return CLibSpider(url).start()


def cist(url):
    return ACistSpider(url).start()
def cistContent(url):
    return CCistSpider(url).start()


def gra(url):
    pass
def graContent(url):
    pass

pattern = re.compile(r'www\.(.*)\.cdut.edu.cn')
switch = {
    'xww': index,
    'ajax': ajax,
    'aao': aao,
    'lib': lib,
    'cist': cist,
    'gra': gra,
}
switchContent = {
    'xww': indexContent,
    'aao': aaoContent,
    'lib': libContent,
    'cist': cistContent,
    'gra': graContent,
}


def startArticle(url):
    if url.endswith('.dwr'):
        return switch.get('ajax')(url)
    result = re.findall(pattern, url)
    if result:
        return switch.get(result[0])(url)
    else:
        return switch.get('xww')(url)

def startContent(url):
    result = re.findall(pattern, url)
    if result:
        return switchContent.get(result[0])(url)
    else:
        return switchContent.get('xww')(url)
