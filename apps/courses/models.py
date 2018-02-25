# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from organization.models import CourseOrg,Teacher

# Create your models here.
class Course(models.Model):
    course_org=models.ForeignKey(CourseOrg,verbose_name=u'课程机构',null=True,blank=True)#新增字段时，不能为空，但数据库已有数据，故增加null＝true
    name=models.CharField(max_length=20,verbose_name=u'课程名')
    desc=models.CharField(max_length=300,verbose_name=u'课程描述')
    detail=models.TextField(verbose_name=u'课程详情')
    degree=models.CharField(choices=(('cj',u'初级'),('zj',u'中级'),('gj',u'高级')),max_length=10)
    learn_times=models.IntegerField(default=0,verbose_name=u'学习时间（分钟数)')
    students=models.IntegerField(default=0,verbose_name=u'学习人数')
    fav_nums=models.IntegerField(default=0,verbose_name=u'收藏人数')
    image=models.ImageField(upload_to='courses/%Y/%m',verbose_name=u'封面图',max_length=100)
    click_nums=models.IntegerField(default=0,verbose_name=u'点击数')
    add_time=models.DateTimeField(default=datetime.now,verbose_name=u'添加时间')
    category = models.CharField(default=u'后端开发',max_length=20, verbose_name=u'课程类别')
    tag=models.CharField(default='',verbose_name=u'课程标签',max_length=20)
    teacher=models.ForeignKey(Teacher,verbose_name=u'讲师',null=True,blank=True)
    youneed_known=models.CharField(default='',max_length=300,verbose_name=u'课程须知')
    teacher_tell=models.CharField(default='',max_length=300,verbose_name=u'老师告诉你能学到什么')
    is_banner=models.BooleanField(default=False,verbose_name=u'是否轮播')

    class Meta:
         verbose_name=u'课程'
         verbose_name_plural=verbose_name

    def get_zj_nums(self):
        #获取课程章节数
        return self.lesson_set.all().count()#有外键指向model时，该model可以反向取数据
    get_zj_nums.short_description=u'章节数'#设置函数的显示名称

    def go_to(self):
        from django.utils.safestring import mark_safe#将超文本解释成为文本
        return mark_safe("<a href='http://www.imooc.com'>跳转</>")
    go_to.short_description=u'跳转'

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        #获取课程所有章节
        return self.lesson_set.all()

    def __unicode__(self):
        return self.name


class BannerCourse(Course):
    class Meta:
        verbose_name=u'轮播课程'
        verbose_name_plural=verbose_name
        proxy=True #若不设置此项，则会再生成一张表轮播课程表
                #这样设置后，不会生成表，但是会具有model的功能

class  Lesson(models.Model):
    course=models.ForeignKey(Course,verbose_name=u'课程')
    name = models.CharField(max_length=20, verbose_name=u'章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    learn_times = models.IntegerField(default=0, verbose_name=u'学习时间（分钟数)')

    class Meta:
         verbose_name=u'章节'
         verbose_name_plural=verbose_name

    def __unicode__(self):
        return self.name

    def get_lesson_video(self):
        #获取章节视频
        return self.video_set.all()


class Video(models.Model):
    lesson=models.ForeignKey(Lesson,verbose_name=u'章节')
    name = models.CharField(max_length=20, verbose_name=u'视频名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    url=models.CharField(max_length=200,verbose_name=u'访问地址',default='')

    class Meta:
         verbose_name=u'视频'
         verbose_name_plural=verbose_name

    def __unicode__(self):
        return self.name


class CourseResource(models.Model):
    course=models.ForeignKey(Course,verbose_name=u'课程')
    name = models.CharField(max_length=100, verbose_name=u'名称')
    download=models.FileField(upload_to='course/resource/%Y/%m',verbose_name=u'资源文件',max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
         verbose_name=u'课程资源'
         verbose_name_plural=verbose_name
