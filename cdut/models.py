import json

import re
from django.db import models

# 用户表
from django.db.models.query_utils import Q
from django.utils import timezone

from utils.util import json_serial


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=64)
    device_platform = models.CharField(blank=True, unique=False, max_length=16)
    device_model = models.CharField(blank=True, unique=False, max_length=16)
    join_time = models.DateTimeField(auto_now_add=True)
    last_visit_time = models.DateTimeField(auto_now=True)
    associate_article_ids = models.TextField(blank=True, unique=False)

    def __str__(self):
        return self.device_id


# 评论表
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    article = models.ForeignKey('Article', unique=False)
    user = models.ForeignKey('User')
    datetime = models.DateTimeField(unique=False, auto_now_add=True)
    tool = models.CharField(blank=True, unique=False, max_length=16)
    message = models.TextField(unique=False)

    def __str__(self):
        return self.message

    def toJson(self):
        item = {}
        item['id'] = self.comment_id
        item['articleId'] = self.article.article_id
        item['userId'] = self.user.user_id
        item['deviceId'] = self.user.device_id
        item['tool'] = self.tool
        item['datetime'] = json_serial(self.datetime)
        item['message'] = self.message
        return item


# 访问次数表
class VisitNum(models.Model):
    visitnum_id = models.AutoField(primary_key=True)
    article = models.ForeignKey('Article')
    pv = models.IntegerField(default=0, unique=False)
    uv = models.IntegerField(default=0, unique=False)

    def __str__(self):
        return '' + self.visitnum_id


# 文章类型表
class Type(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=8)

    def __str__(self):
        return self.name


# 文章来源表
class Source(models.Model):
    source_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=16)
    tag = models.CharField(max_length=8)

    def __str__(self):
        return self.name


# 文章附件表
class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    content = models.ForeignKey('Content')
    url = models.URLField()
    name = models.CharField(blank=True, unique=False, max_length=64)
    type = models.CharField(unique=False, max_length=8)

    def __str__(self):
        return self.name

    def toJson(self):
        item = {}
        item['id'] = self.file_id
        item['url'] = self.url
        item['name'] = self.name
        item['type'] = self.type
        return item


# 文章数据表
class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    source = models.ForeignKey('Source', unique=False)
    type = models.ForeignKey('Type', unique=False)
    title = models.TextField()
    origin_url = models.URLField()
    author = models.CharField(blank=True, unique=False, max_length=32)
    addtime = models.DateTimeField(unique=False, auto_now_add=True)

    def __str__(self):
        return self.title

    def toJson(self):
        _item = {}
        _item['id'] = self.article_id
        _item['title'] = self.title
        _item['author'] = self.author
        _item['url'] = self.origin_url
        _item['time'] = json_serial(self.addtime)
        _item['source'] = Source.objects.get(source_id=self.source_id).name
        _item['type'] = Type.objects.get(type_id=self.type_id).name
        try:
            content = Content.objects.get(article_id=self.article_id)
            pattern = re.compile(r'{"img": "(.*?)"}')
            urls = re.findall(pattern,content.content)
            if urls:
                _item['img'] = urls[0]
        except Content.DoesNotExist:
            pass
        return _item


# 文章内容表
class Content(models.Model):
    content_id = models.AutoField(primary_key=True)
    article = models.ForeignKey('Article')
    content = models.TextField(blank=True)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

    def toJson(self):
        item = {}
        item['id'] = self.content_id
        item['content'] = self.content
        item['dateTime'] = json_serial(self.datetime)
        return item
