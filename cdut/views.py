import json
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from redis._compat import unicode

from cdut.models import Article, User, Content, File, Type, Source
from spider import dispatcher
from spider.article_spider import AAaoSpider, ABase
from spider.content_spider import CAaoSpider, CBase
from spider.static import entry_url


# 多线程分3步：
# 1、多线程开启所有网址的列表抓取，获得article对象列表；
# 2、依据url从数据库判断是否已存在进而筛选出新增对象列表；
# 3、依据列表的大小判断多线程数量开启Map的内容抓取，获得content对象列表；
# 4、单线程批量存储Article，Content，file
from utils.util import json_serial


def index(request):
    starttime = datetime.now()
    totalArticle = []
    totalURL = []
    totalAid = []
    # ----------------------------------------------------------1
    pool = ThreadPool(processes=6)
    results = pool.map(dispatcher.startArticle, entry_url)
    pool.close()
    pool.join()
    # ----------------------------------------------------------2
    for list in results:
        totalArticle.extend(list.cList)
    for article in totalArticle:
        if ABase.is_article_exists(article.origin_url):
            tmp = Article.objects.get(origin_url=article.origin_url)
            print('exsit article: ', tmp.article_id)
            totalAid.append(tmp.article_id)
        else:
            print('add article')
            article.save()  # 存储之后才有ID，并不是由save方法返回！！！
            totalAid.append(article.article_id)
    tmpTotalAid = totalAid
    totalAid = []
    for i in range(len(tmpTotalAid)):
        if not CBase.is_content_exists(tmpTotalAid[i]):
            print('add aid: ', tmpTotalAid[i])
            totalAid.append(tmpTotalAid[i])
            totalURL.append(totalArticle[i].origin_url)
    print('totalURL: ', totalURL)
    print('totalAid: ', totalAid)
    # ----------------------------------------------------------3
    if totalURL:
        if len(totalURL) < 5:
            threadNum = len(totalURL)
        else:
            threadNum = len(totalURL) // 2
        pool = ThreadPool(processes=threadNum)
        results = pool.map(dispatcher.startContent, totalURL)
        pool.close()
        pool.join()
        print('content result= ', len(results))
        # ----------------------------------------------------------4
        for i in range(len(results)):
            content_id = results[i].save(totalAid[i])
            if content_id and results[i].file_url:
                results[i].savefile(content_id)

    # print(datetime.now()-starttime)
    return HttpResponse(datetime.now() - starttime)


###
# 支持post && get
###
@csrf_exempt
def getNewsList(request):
    _type = request.GET.get('_type')
    _source = request.GET.get('_source')
    _startId = request.GET.get('_startId')
    _pageNum = request.GET.get('_pageNum')
    # if not _startId:
    #     return HttpResponse(json.dumps(baseJSON(False, '_startId不能为空')), content_type="application/json")
    addOrUpdateUser(request)
    if not _pageNum:
        _pageNum = 10
    try:
        type = Type.objects.get(type_id=_type) if _type else None
        source = Source.objects.get(source_id=_source) if _source else None
    except Type.DoesNotExist:
        return HttpResponse(json.dumps(baseJSON(False, '_type参数错误')), content_type="application/json")
    except Source.DoesNotExist:
        return HttpResponse(json.dumps(baseJSON(False, '_source参数错误')), content_type="application/json")
    args = {}
    if type:
        args['type'] = type
    if source:
        args['source'] = source
    if _startId:
        args['article_id__gte'] = _startId
        args['article_id__lte'] = int(_startId)+int(_pageNum)
    cursor = Article.objects.filter(**args)
    data = []
    for item in cursor:
        if len(data) >= _pageNum:
            break
        data.append(item.toJson())
    return HttpResponse(json.dumps(baseJSON(True, '请求成功', data=data)), content_type="application/json")
    # result = json.loads(content[0].content)
    # if isinstance(cursor[0].title, unicode):
    # _title = cursor[0].title
    # .encode('utf-8').decode('unicode_escape')
    # return render(request, 'muban.html', {'title': _title, 'content': result})

@csrf_exempt
def getNews(request):
    _aid = request.GET.get('_aid')
    data = {}
    if not _aid:
        return HttpResponse(json.dumps(baseJSON(False, '参数不能为空')), content_type="application/json")
    try:
        _article = Article.objects.get(article_id=_aid)
    except Article.DoesNotExist:
        return HttpResponse(json.dumps(baseJSON(False, '未找到')), content_type="application/json")
    try:
        _content = Content.objects.get(article=_article)
    except Content.DoesNotExist:
        return HttpResponse(json.dumps(baseJSON(False, '文章已删除')), content_type="application/json")
    try:
        _file = File.objects.get(content_id=_content)
    except File.DoesNotExist:
        _file = None
    data['article'] = _article.toJson()
    data['content'] = _content.toJson()
    data['file'] = _file.toJson() if _file else {}
    return HttpResponse(json.dumps(baseJSON(True, '请求成功', data=data)), content_type="application/json")

def addComment(request):
    pass

def getFile(request):
    pass

@csrf_exempt
def addOrUpdateUser(request):
    deviceId = request.META.get('HTTP_ID')
    devicePlatform = request.META.get('HTTP_PLATFORM')
    deviceModel = request.META.get('HTTP_MODEL')
    if not deviceId:
        return HttpResponse('none')
    try:
        User.objects.get(device_id=deviceId).save()
        return HttpResponse('')
    except User.DoesNotExist:
        args = {}
        args['device_id'] = deviceId
        args['device_platform'] = devicePlatform
        if deviceModel:
            args['device_model'] = deviceModel
        user = User(**args)
        user.save()
        return user.user_id


def baseJSON(isTrue, msg, data=None):
    _json = {}
    _json['result'] = isTrue
    _json['msg'] = msg
    if data:
        _json['data'] = data
    else:
        _json['data'] = {}
    return _json


def push(request):
    import jpush as jpush
    app_key = u'd6bdfb193bf44f78d78300ee'
    master_secret = u'1ec81f183f8fcf37fec1ca90'
    _jpush = jpush.JPush(app_key, master_secret)

    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="Hello, world!")
    push.platform = jpush.all_
    push.send()
    return HttpResponse('success!')
