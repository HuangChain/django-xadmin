#coding:utf-8
import xadmin
from .models import EmailVerify,Banner
from xadmin import views


class BaseSetting(object):
    enable_themes=True
    use_bootswatch=True

class GlobleSettings(object):
    site_title=u'慕学后台管理系统'
    site_footer=u'慕学在线网'
    menu_style='accordion'

class EmailVerifyAdmin(object):
    list_display=['code','email','send_type','send_time']
    search_fields=['code','email','send_type']#不能对时间search，否则会出错
    list_filter=['code','email','send_type','send_time']
    model_icon='fa fa-user'#可在font awesome官网寻找自己喜欢的相应版本的图标

class BannerAdmin(object):
    list_display=['title','image','url','index','add_time']
    search_fields=['title','image','url','index']
    list_filter=['title','image','url','index','add_time']

xadmin.site.register(EmailVerify,EmailVerifyAdmin)
xadmin.site.register(Banner,BannerAdmin)
xadmin.site.register(views.BaseAdminView,BaseSetting)
xadmin.site.register(views.CommAdminView,GlobleSettings)