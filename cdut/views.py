from django.http.response import HttpResponse

from spider.article_spider import AIndexSpider, AAaoSpider
from spider.content_spider import CIndexSpider
from spider.static import entry_url


def index(request):
    for url in entry_url:
        spider = AIndexSpider(url)
        spider.start()
        for i in range(len(spider.aid)):
            contentspider = CIndexSpider(''+spider.aref[i], spider.aid[i])
            contentspider.start()
    return HttpResponse('欢迎!!!')
def content(request):
    contentspider = CIndexSpider(r'http://www.cdut.edu.cn/xww/news/145732274461961636.html','1')
    contentspider.start()
    return HttpResponse('content')
def aao(request):
    spider = AAaoSpider(r'http://www.aao.cdut.edu.cn/aao/aao.php?sort=389&sorid=391&from=more')
    spider.start()
    return HttpResponse('aao')

def msgs(request):
    pass
    # return HttpResponse(serializers.serialize("json", Notice.objects.all()),content_type="application/json")
