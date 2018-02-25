#coding:utf-8
import xadmin
from .models import Course,Lesson,Video,CourseResource,BannerCourse
from organization.models import CourseOrg

class LesssonInline(object):
    model=Lesson
    extra=0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    list_display=['name','desc','detail','degree','learn_times','students','click_nums','get_zj_nums','go_to']
    search_fields=['name','desc','detail','degree','students']#不能对时间search，否则会出错
    list_filter=['name','desc','detail','degree','learn_times','students']
    model_icon = 'fa fa-user'  # 可在font awesome官网寻找自己喜欢的相应版本的图标
    ordering=['-click_nums']
    readonly_fields=['click_nums']#设置只读
    list_editable=['degree']#设置为可在列表页直接编辑
    exclude=['fav_nums']#隐藏某字段
    inlines=[LesssonInline,CourseResourceInline]#同一个model注册两个管理器，在course里面嵌套lesson（只能单次嵌套）
    #refresh_times=[3,5] #设置自动刷新秒数，例如需要实时观察数据时

    def queryset(self):#同一张表，分类管理，完成数据的分类管理，一个管理轮播图，一个管理非轮播图
        qs=super(CourseAdmin,self).queryset()
        qs=qs.filter(is_banner=False)
        return qs

    def save_models(self):#重载
        #在保存课程的时候重新统计课程机构的课程数
        obj=self.new_obj # new一个course对象
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org  # course有一个外键course_org
            course_org.course_nums=Course.objects.filter(course_org=course_org).count()
            course_org.save()

class BannerCourseAdmin(object):
    list_display=['name','desc','detail','degree','learn_times','students','click_nums']
    search_fields=['name','desc','detail','degree','students']#不能对时间search，否则会出错
    list_filter=['name','desc','detail','degree','learn_times','students']
    model_icon = 'fa fa-user'  # 可在font awesome官网寻找自己喜欢的相应版本的图标
    ordering=['-click_nums']
    readonly_fields=['click_nums']#设置只读
    exclude=['fav_nums']#隐藏某字段
    inlines=[LesssonInline,CourseResourceInline]#在course里面嵌套lesson（只能单次嵌套）

    def queryset(self):#重载方法
        qs=super(BannerCourseAdmin,self).queryset()#继承父类queryset方法
        qs=qs.filter(is_banner=True)#获取is_banner=True是轮播图的数据
        return qs


class LessonAdmin(object):
    list_display=['course','name','add_time']
    search_fields=['course','name']
    list_filter=['course__name','name','add_time']

class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']

class CourseResourceAdmin(object):
    list_display = ['course', 'name','download','add_time']
    search_fields = ['course', 'name','download']
    list_filter = ['course', 'name','download','add_time']


xadmin.site.register(Course,CourseAdmin)
xadmin.site.register(BannerCourse,BannerCourseAdmin)
xadmin.site.register(Lesson,LessonAdmin)
xadmin.site.register(Video,VideoAdmin)
xadmin.site.register(CourseResource,CourseResourceAdmin)