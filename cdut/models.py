#与数据库操作相关，存入或读取数据时用到这个，当然用不到数据库的时候 你可以不使用
from django.db import models


class Notice(models.Model):
    title = models.TextField()
    url = models.URLField()
    time = models.TextField()