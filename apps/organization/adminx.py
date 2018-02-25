#coding:utf-8
import xadmin
from .models import CityDict,CourseOrg,Teacher

class CityDictAdmin(object):
    list_display=['name','desc','add_time']
    search_fields=['name','desc']
    list_filter=['name','desc','add_time']

class CourseOrgAdmin(object):
    list_display=['name','desc','click_nums','fav_nums']
    search_fields=['name','desc','click_nums','fav_nums']
    list_filter=['name','desc','click_nums','fav_nums']
    refield_style='fk-ajax'#此版本未生效
    #courseorg是course的外键，此设置可使数据不至于一次性加载出来，而是根据输入的字段来加载

class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_year', 'work_company']
    search_fields = ['org', 'name', 'work_year', 'work_company']
    list_filter = ['org', 'name', 'work_year', 'work_company']


xadmin.site.register(CityDict,CityDictAdmin)
xadmin.site.register(CourseOrg,CourseOrgAdmin)
xadmin.site.register(Teacher,TeacherAdmin)
