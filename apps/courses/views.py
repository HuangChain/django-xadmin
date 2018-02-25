# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.base import View
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q

from .models import Course,CourseResource
from operation.models import UserFavorite,CourseComments,UserCourse
from utils.mixin_utils import LoginRequiredMixin
# Create your views here.
class CourseListView(View):
    def get(self,request):
        all_courses=Course.objects.all().order_by("-add_time")
        hot_courses=Course.objects.all().order_by("-click_nums")[:3]
        search_keywords=request.GET.get('keywords','')
        if search_keywords:
            all_courses=all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))#i表示不区分大小写
                                                            #查询__lte<=,__gte>=,__表示对前面的字段进行操作
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_courses = all_courses.order_by('-students')
        elif sort == 'courses':
            all_courses = all_courses.order_by('-click_nums')
        #分页
        paginator = Paginator(all_courses,6)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)#取第page页的数据
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        return render(request,'course-list.html',{
            'all_courses':contacts,
            'contacts': contacts,
            'sort':sort,
            'hot_courses':hot_courses
        })


class CourseDetailView(View):
    """
    课程详情页
    """
    def get(self,request,course_id):
        course=Course.objects.get(id=int(course_id))
        #增加课程点击数
        course.click_nums+=1
        course.save()
        has_fav_course=False
        has_fav_org=False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=course_id,fav_type=1):
                has_fav_course=True
            if UserFavorite.objects.filter(user=request.user,fav_id=course.course_org.id,fav_type=2):
                has_fav_org = True
        tag=course.tag
        if tag:
            relate_courses=Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses=[]#因为前端用了for遍历，故不能返回字符串，要返回字典
        return render(request,'course-detail.html',{
            'course':course,
            'relate_courses':relate_courses,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org
        })


class CourseInfoView(LoginRequiredMixin,View):
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))
        course.students+=1
        course.save()
        #查询用户是否已经关联了该课程
        user_courses=UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            user_courses=UserCourse(user=request.user,course=course)
            user_courses.save()
        # 取出UserCourse表，学习过该课程的所有用户课程记录
        user_courses=UserCourse.objects.filter(course=course)
        # python列表式，学习过该课程的所有用户的id
        user_ids=[user_course.user.id for user_course in user_courses]
        #所有用户学习过的所有课程
        all_user_courses=UserCourse.objects.filter(user_id__in=user_ids)#user是外键，＋_把id传进来，而不用去传实例
                                                                        #__in django model用法，只要user_id在user_ids里面，就会返回所有列表
        #python列表式，学习过该课程的所有用户学习过的课程id
        course_ids=[user_course.course.id for user_course in user_courses]
        #取出学习过该课程的所有用户学习过的课程记录
        relate_courses=Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        all_resources=CourseResource.objects.filter(course=course)
        return render(request,'course-video.html',{
            "course": course,
            'all_resources':all_resources,
            'relate_courses':relate_courses
        })


class CommentsView(LoginRequiredMixin,View):#从左到右表示继承顺序
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources=CourseResource.objects.filter(course=course)
        all_comments=CourseComments.objects.all()
        return render(request,'course-comment.html',{
            "course": course,
            'all_resources':all_resources,
            'all_comments':all_comments
        })

class AddCommentsView(View):
    """
    用户添加课程评论
    """
    def post(self,request):
        if not request.user.is_authenticated():
            return JsonResponse({"status":"fail","msg":u"用户未登陆"})
        course_id=request.POST.get('course_id',0)
        comments=request.POST.get('comments','')
        if course_id>0 and comments:
            course_comments=CourseComments()
            course=Course.objects.get(id=int(course_id))
            course_comments.course=course
            course_comments.comments=comments
            course_comments.user=request.user
            course_comments.save()
            return JsonResponse({"status":"success","msg":u"添加成功"})
        else:
            return JsonResponse({"status":"fail","msg":u"添加失败"})
