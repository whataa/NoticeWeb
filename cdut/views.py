from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

from django.http.response import HttpResponse

from cdut.models import Article
from spider import dispatcher
from spider.article_spider import AAaoSpider, ABase
from spider.content_spider import CAaoSpider, CBase
from spider.static import entry_url

#多线程分3步：
#1、多线程开启所有网址的列表抓取，获得article对象列表；
#2、依据url从数据库判断是否已存在进而筛选出新增对象列表；
#3、依据列表的大小判断多线程数量开启Map的内容抓取，获得content对象列表；
#4、单线程批量存储Article，Content，file
def index(request):
    starttime = datetime.now()
    totalArticle = []
    totalURL = []
    totalAid = []
    #----------------------------------------------------------1
    pool = ThreadPool(processes=4)
    results = pool.map(dispatcher.startArticle, entry_url)
    pool.close()
    pool.join()
    #----------------------------------------------------------2
    for list in results:
        totalArticle.extend(list.cList)
    for article in totalArticle:
        if ABase.is_article_exists(article.origin_url):
            tmp = Article.objects.get(origin_url=article.origin_url)
            print('exsit article,return the id')
            totalAid.append(tmp.article_id)
        else:
            print('add article')
            totalAid.append(article.save())
    tmpTotalAid = totalAid
    totalAid = []
    for i in range(len(tmpTotalAid)):
        if not CBase.is_content_exists(tmpTotalAid[i]):
            totalAid.append(tmpTotalAid[i])
            totalURL.append(totalArticle[i].origin_url)
    print(totalURL)
    #----------------------------------------------------------3
    if totalURL:
        if len(totalURL)<5:
            threadNum = len(totalURL)
        else:
            threadNum = len(totalURL)//2
        pool = ThreadPool(processes=threadNum)
        results = pool.map(dispatcher.startContent, totalURL)
        pool.close()
        pool.join()
        print(len(results))
    #----------------------------------------------------------4
        for i in range(len(results)):
            content_id = results[i].save(totalAid[i])
            if content_id and results[i].file_url:
                results[i].savefile(content_id)

    # print(datetime.now()-starttime)
    return HttpResponse(datetime.now()-starttime)


