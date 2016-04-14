"""NoticeWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from cdut import views

urlpatterns = [
    url(r'^user/$',views.addOrUpdateUser),
    url(r'^comment/list/$',views.getCommentList),
    url(r'^comment/$',views.addComment),
    url(r'^news/$',views.getNews),
    url(r'^news/list/$',views.getNewsList),
    url(r'^push/$',views.push),
    url(r'^$', views.index),
    url(r'^admin/', admin.site.urls),
]
