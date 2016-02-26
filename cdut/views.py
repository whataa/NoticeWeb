from django.http.response import HttpResponse

from spider.article_spider import AIndexSpider
from spider.content_spider import CIndexSpider
from spider.static import entry_url


def index(request):
    for url in entry_url:
        spider = AIndexSpider(url)
        spider.start()
        for i in range(len(spider.aid)):
            contentspider = CIndexSpider(spider.aref[i], spider.aid[i])
            contentspider.start()
    return HttpResponse('欢迎!!!')

def msgs(request):
    pass
    # return HttpResponse(serializers.serialize("json", Notice.objects.all()),content_type="application/json")
