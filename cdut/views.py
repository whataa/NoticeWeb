from django.http.response import HttpResponse

from spider.cdut_default import DefaultSpider


def index(request):
    spider = DefaultSpider(u'http://www.cdut.edu.cn/xww/news2_tzgg.html')
    spider.start()
    print(spider.aid)
    print(spider.aref)
    return HttpResponse('欢迎!!!')

def msgs(request):
    pass
    # return HttpResponse(serializers.serialize("json", Notice.objects.all()),content_type="application/json")
