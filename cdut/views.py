from django.http.response import HttpResponse

from spider.article_spider import AIndexSpider, AAaoSpider
from spider.content_spider import CIndexSpider, CAaoSpider
from spider.static import entry_url


def index(request):
    for url in entry_url:
        spider = AIndexSpider(url)
        spider.start()
        for i in range(len(spider.aid)):
            contentspider = CIndexSpider(''+spider.aref[i], spider.aid[i])
            contentspider.start()
    return HttpResponse('欢迎!!!')
def aao(request):
    spider = AAaoSpider(r'http://www.aao.cdut.edu.cn/aao/aao.php?sort=389&sorid=391&from=more')
    spider.start()
    for i in range(len(spider.aid)):
        aaospider = CAaoSpider(''+spider.aref[i], spider.aid[i])
        aaospider.start()
    return HttpResponse('aao')

def msgs(request):
    pass
    # return HttpResponse(serializers.serialize("json", Notice.objects.all()),content_type="application/json")
