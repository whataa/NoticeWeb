import re

from spider.article_spider import AIndexSpider, AAaoSpider
from spider.content_spider import CIndexSpider, CAaoSpider


def index(url):
    return AIndexSpider(url).start()
def indexContent(url):
    return CIndexSpider(url).start()
    pass

def aao(url):
    return AAaoSpider(url).start()
def aaoContent(url):
    return CAaoSpider(url).start()
    pass

def lib(url):
    pass
def libContent(url):
    pass

def cist(url):
    pass
def cistContent(url):
    pass

def gra(url):
    pass
def graContent(url):
    pass

pattern = re.compile(r'www\.(.*)\.cdut.edu.cn')
switch = {
    'xww': index,
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
