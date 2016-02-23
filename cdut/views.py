#处理用户发出的请求，从urls.py中对应过来, 通过渲染templates中的网页可以将显示内容，
#比如登陆后的用户名，用户请求的数据，输出到网页
import json

from django.core import serializers
from django.http.response import HttpResponse
from django.shortcuts import render

from cdut.models import Notice
from spider.cdut_default import DefaultSpider


def index(request):
    DefaultSpider(u'http://www.cdut.edu.cn/xww/news2_tzgg.html').getNotice()
    return HttpResponse('欢迎!!!')

def msgs(request):
    # Notice.objects.all().values()
    return HttpResponse(serializers.serialize("json", Notice.objects.all()),content_type="application/json")