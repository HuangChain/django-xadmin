#coding:utf-8
"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url,include
from django.contrib import admin
from django.views.generic import TemplateView  #处理静态文件
from django.views.static import serve
import xadmin

# from users.views import user_login
# from users.views import LoginUnSafeView
from users.views import LoginView,RegisterView,IndexView
from users.views import ActiveUserView,ForgetPwdView,ResetView1,ResetView2,LogoutView
from organization.views import OrgView
from MxOnline.settings import MEDIA_ROOT
urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$',IndexView.as_view(),name='index'),
   #url(r'^$',TemplateView.as_view(template_name='index.html'),name='index'),#调用类的as_view方法，将templates转换成view
   #url(r'^login/$',TemplateView.as_view(template_name='login.html'),name='login'),#不需要写后台的view，django会自动跳转到login.html
   #url(r'^login/$',user_login,name='login'),
    # url(r'^login/$',LoginUnSafeView.as_view(),name='login'),
    url(r'^login/$',LoginView.as_view(),name='login'),
    url(r'^logout/$',LogoutView.as_view(),name='logout'),
    url(r'^register/$',RegisterView.as_view(),name='register'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$',ActiveUserView.as_view(),name='user_active'),#?P提取<>里面变量当作参数，提取出.*正则表达式，放到变量里面
    url(r'^forget/$',ForgetPwdView.as_view(),name='forget'),
    url(r'^reset/(?P<reset_code>.*)/$',ResetView1.as_view(),name='reset1'),
    url(r'^reset/$',ResetView2.as_view(),name='reset2'),

    url(r'^media/(?P<path>.*)$',serve,{'document_root':MEDIA_ROOT}),#配置上传文件的访问处理函数
    #debug=false时，表示生产环境，ngix等会自动加载静态文件，所以django的static会自动失效，故需自己写static的url使其重新生效
    # url(r'^static/(?P<path>.*)$',serve,{'document_root':STATIC_ROOT}),

    #课程机构url配置
    url(r'^org/', include('organization.urls', namespace="org")),
    #课程相关url配置
    url(r'^course/', include('courses.urls', namespace="course")),
    url(r'^users/', include('users.urls', namespace="users")),
    #富文本相关url
    #url(r'^ueditor/',include('DjangoUeditor.urls' )),



]

#全局404页面配置
handler404='users.views.page_not_found'
handler500='users.views.page_error'