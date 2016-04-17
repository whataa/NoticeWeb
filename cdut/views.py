import json
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

from django.db.models import Q
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from cdut.models import Article, User, Content, File, Type, Source, Comment
from spider import dispatcher
from spider.article_spider import ABase
from spider.content_spider import CBase
from spider.static import entry_url


# 多线程分3步：
# 1、多线程开启所有网址的列表抓取，获得article对象列表；
# 2、依据url从数据库判断是否已存在进而筛选出新增对象列表；
# 3、依据列表的大小判断多线程数量开启Map的内容抓取，获得content对象列表；
# 4、单线程批量存储Article，Content，file


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
        push(len(totalURL))
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


# 获取信息列表
# 1.无_pageNum参数则默认每页数量10
# 2.无_startId参数则默认从最新ID开始
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
        args['article_id__gte'] = int(_startId)-int(_pageNum)
        args['article_id__lte'] = _startId
    cursor = Article.objects.order_by('-article_id').filter(**args)
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

# 获取信息详情
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

# 添加评论
@csrf_exempt
def addComment(request):
    _articleId = request.GET.get('_articleId')
    _tool = request.GET.get('_tool')
    _msg = request.GET.get('_msg')
    _user = addOrUpdateUser(request)
    if not _user:
        return HttpResponse(json.dumps(baseJSON(False, '没有该用户')), content_type="application/json")
    try:
        _id = Article.objects.get(article_id=_articleId)
    except Article.DoesNotExist:
        return HttpResponse(json.dumps(baseJSON(False, '文章已删除')), content_type="application/json")
    if not _msg:
        return HttpResponse(json.dumps(baseJSON(False, '评论不能为空')), content_type="application/json")
    arg = {}
    if _tool:
        arg['tool'] = _tool
    arg['article_id'] = _id.article_id
    arg['user_id'] = _user
    arg['message'] = _msg
    comment = Comment(**arg)
    comment.save()
    return HttpResponse(json.dumps(baseJSON(True, '评论成功')), content_type="application/json")

# 获取评论列表
@csrf_exempt
def getCommentList(request):
    _articleId = request.GET.get('_articleId')
    _userId = request.GET.get('_userId')
    _startId = request.GET.get('_startId')
    _pageNum = request.GET.get('_pageNum')
    if not _pageNum:
        _pageNum = 10
    if _userId:
        user = getUser(request)
        if not user:
            return HttpResponse(json.dumps(baseJSON(False, '没有该用户')), content_type="application/json")
    else:
        user = None
    if _articleId:
        try:
            article = Article.objects.get(article_id=_articleId)
        except Article.DoesNotExist:
            return HttpResponse(json.dumps(baseJSON(False, '文章已删除')), content_type="application/json")
    else:
        article = None
    args = {}
    if _startId:
        args['comment_id__lte'] = _startId
    if user:
        args['user_id'] = user.user_id
    if article:
        args['article_id'] = article.article_id
    cursor = Comment.objects.order_by('-comment_id').filter(**args)
    data = []
    for item in cursor:
        if len(data) >= _pageNum:
            break
        data.append(item.toJson())
    return HttpResponse(json.dumps(baseJSON(True, '请求成功', data=data)), content_type="application/json")

#获取热门列表
def getHotNews(request):
    cursor = Comment.objects.raw('SELECT * FROM cdut_comment GROUP BY article_id HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC')
    ids = []
    for comment in cursor:
        ids.append(comment.article_id)
    result = []
    if ids:
        result = Article.objects.filter(
            article_id__in=ids
        )
    data = []
    for item in result:
        if len(data) >= 10:
            break
        data.append(item.toJson())
    return HttpResponse(json.dumps(baseJSON(True, '请求成功',data=data)), content_type="application/json")

@csrf_exempt
def doSearch(request):
    param = request.GET.get('_param')
    pageNum = request.GET.get('_pageNum')
    if not pageNum:
        pageNum = 10
    if not param:
        return HttpResponse(json.dumps(baseJSON(False, '条件不能为空')), content_type="application/json")
    cursor = Article.objects.filter(
        Q(title__contains=param)|Q(author__contains=param)|Q(addtime__contains=param)
    ).order_by('-addtime')
    data = []
    for item in cursor:
        if len(data) >= pageNum:
            break
        data.append(item.toJson())
    return HttpResponse(json.dumps(baseJSON(True, '请求成功', data=data)), content_type="application/json")


# 获取用户信息，仅供内部调用
def getUser(request):
    userId = request.GET.get('_userId')
    try:
        user = User.objects.get(user_id=userId)
        return user
    except User.DoesNotExist:
        return None

def getFile(request):
    pass

# 新增/更新用户信息，仅供内部调用
@csrf_exempt
def addOrUpdateUser(request):
    deviceId = request.META.get('HTTP_ID')
    devicePlatform = request.META.get('HTTP_PLATFORM')
    deviceModel = request.META.get('HTTP_MODEL')
    if not deviceId:
        return None
    try:
        user = User.objects.get(device_id=deviceId)
        user.save()
        return user.user_id
    except User.DoesNotExist:
        args = {}
        args['device_id'] = deviceId
        args['device_platform'] = devicePlatform
        if deviceModel:
            args['device_model'] = deviceModel
        user = User(**args)
        user.save()
        return user.user_id

# json模板
def baseJSON(isTrue, msg, data=None):
    _json = {}
    _json['result'] = isTrue
    _json['msg'] = msg
    if data:
        _json['data'] = data
    else:
        _json['data'] = {}
    return _json

# 推送
def push(num):
    import jpush as jpush
    app_key = u'd6bdfb193bf44f78d78300ee'
    master_secret = u'1ec81f183f8fcf37fec1ca90'
    _jpush = jpush.JPush(app_key, master_secret)

    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="update: "+str(num))
    push.platform = jpush.all_
    push.send()
