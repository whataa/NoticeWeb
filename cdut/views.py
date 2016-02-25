from django.http.response import HttpResponse

from spider.article_spider import AIndexSpider
from spider.content_spider import CIndexSpider


def index(request):
    spider = AIndexSpider(u'http://www.cdut.edu.cn/xww/news2_zl.html')
    spider.start()
    print(spider.aid)
    print(spider.aref)
    for i in range(len(spider.aid)):
        contentspider = CIndexSpider(spider.aref[i], spider.aid[i])
        contentspider.start()
    return HttpResponse('欢迎!!!')

def msgs(request):
    pass
    # return HttpResponse(serializers.serialize("json", Notice.objects.all()),content_type="application/json")
