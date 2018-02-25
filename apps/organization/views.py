# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.db.models import Q
from pure_pagination import Paginator,EmptyPage,PageNotAnInteger

from organization.models import CourseOrg,CityDict,Teacher
from operation.models import UserFavorite
from courses.models import Course
from organization.form import UserAskForm
# Create your views here.
class OrgView(View):

    def get(self,request):
        all_orgs=CourseOrg.objects.all()
        all_cities=CityDict.objects.all()
        hot_orgs=all_orgs.order_by('-click_nums')[:3]
        # 机构搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))
        sort=request.GET.get('sort','')
        if sort=='students':
            all_orgs=all_orgs.order_by('-students')
        elif sort=='courses':
            all_orgs=all_orgs.order_by('-course_num')
        #筛选城市
        city_id=request.GET.get('city','')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
        #筛选类别
        category=request.GET.get('ct','')
        if category:
            all_orgs = all_orgs.filter(category=category)
        org_nums = all_orgs.count()
        #分页
        try:
            page=request.GET.get('page',1)
        except PageNotAnInteger:
            page=1
        p=Paginator(all_orgs,3,request=request)#对all_org进行分页,每页5条数据
        orgs=p.page(page)#取第page页的数据
        return render(request,'org-list.html',{
            'all_orgs':orgs,
            'all_cities':all_cities,
            'org_nums':org_nums,
            'city_id':city_id,
            'category':category,
            'hot_orgs':hot_orgs,
            'sort':sort
        })


class  AddUserAskView(View):
    def post(self,request):
        userask_form=UserAskForm(request.POST)
        if userask_form.is_valid():
            userask= userask_form.save(commit=True)#本身就是model，故不用把field取出来，直接提交Form到数据库并保存
            #return HttpResponse("{'status':'success'}",content_type='application/json')#指明字符串格式为json
            return JsonResponse({'status': 'success'})
        else:
            # return HttpResponse("{'status':'fail','msg':u'添加出错'}",content_type='application/json')
            print userask_form.errors
            return  JsonResponse({'status':'fail','msg':'添加错误'})#,"value":userask_form.errors


class OrgHomeView(View):
    def get(self,request,org_id):
        current_page='home'
        course_org=CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums+=1
        course_org.save()
        has_fav=False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=course_org.id):
                has_fav=True
        #有外键指向model时，该model可以反向取
        all_courses=course_org.course_set.all()[:3]#小写class名称_set,反向取所有的course，这样就将所有的课程取出来了（course_org是CourseOrg的外键）
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page':current_page,
            'has_fav':has_fav
        })


class OrgCourseView(View):
    def get(self,request,org_id):
        current_page='course'
        course_org=CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id):
                has_fav = True
        all_courses=course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page':current_page,
            'has_fav':has_fav
        })


class OrgDescView(View):
    def get(self,request,org_id):
        current_page='desc'
        course_org=CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page':current_page,
            'has_fav':has_fav
        })




class OrgTeacherView(View):
    def get(self,request,org_id):
        current_page='teacher'
        course_org=CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'course_org': course_org,
            'current_page':current_page,
            'all_teachers':all_teachers,
            'has_fav':has_fav
        })


class AddFavView(View):
    def post(self,request):
        fav_id=request.POST.get('fav_id',0)
        fav_type=request.POST.get('fav_type',0)
        if not request.user.is_authenticated():
            return JsonResponse({"status": "fail", "msg": u"用户未登陆"})
        exist_records=UserFavorite.objects.filter(user=request.user,fav_id=int(fav_id),fav_type=int(fav_type))
        if exist_records:
            #若记录存在，则表示取消收藏
            exist_records.delete()
            if int(fav_type)==1:
                course=Course.objects.get(id=int(fav_id))
                course.fav_nums-=1
                if course.fav_nums < 0:
                    course.fav_nums=0
                course.save()
            elif int(fav_type)==2:
                course_org=Course.objects.get(id=int(fav_id))
                course_org.fav_nums-=1
                if course_org.fav_nums < 0:
                    course_org.fav_nums=0
                course_org.save()
            elif int(fav_type)==3:
                teacher=Course.objects.get(id=int(fav_id))
                teacher.fav_nums-=1
                if teacher.fav_nums < 0:
                    teacher.fav_nums=0
                teacher.save()
            #return HttpResponse('{"status":"success","msg":u"收藏"}', content_type="application/json")
            return JsonResponse({"status": "success", "msg": u"未收藏"})
        else:
            user_fav=UserFavorite()
            if int(fav_id)>0 and int(fav_type)>0:
                user_fav.user=request.user
                user_fav.fav_id=int(fav_id)
                user_fav.fav_type=int(fav_type)
                user_fav.save()
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = Course.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Course.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                #return HttpResponse('{"status":"success","msg":u"已收藏"}', content_type="application/json")
                return JsonResponse({"status":"success","msg":u"已收藏"})
            else:
                #return HttpResponse('{"status":"fail","msg":u"用户未登陆"}',content_type="application/json")
                return JsonResponse({"status":"fail","msg":u"收藏出错"})



class TeacherListView(View):
    """
    课程讲师列表页
    """
    def get(self,request):
        all_teachers=Teacher.objects.all()
        # 讲师搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords) |
                                               Q(work_company__icontains=search_keywords)|
                                               Q(work_position__icontains=search_keywords))
        sort=request.GET.get('sort','')
        if sort:
            if sort=='hot':
                all_teachers=all_teachers.order_by('-click_nums')
        sorted_teachers=Teacher.objects.all().order_by('-click_nums')[:3]
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_teachers, 1, request=request)  # 对all_org进行分页,每页5条数据
        teachers = p.page(page)  # 取第page页的数据
        print teachers
        return render(request,'teachers-list.html',{
            'all_teachers': teachers,
            'sorted_teachers':sorted_teachers,
            'sort':sort
        })


class TeacherDetailView(View):
    def get(self,request,teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums+=1
        teacher.save()
        all_courses=Course.objects.filter(teacher=teacher)
        has_org_fav=False
        if UserFavorite.objects.filter(user=request.user,fav_type=2,fav_id=teacher.org.id):
            has_org_fav=True
        has_teacher_fav = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_fav = True

        sorted_teachers = Teacher.objects.all().order_by('-click_nums')[:3]
        return render(request,'teacher-detail.html',{
            'teacher':teacher,
            'all_courses':all_courses,
            'sorted_teachers': sorted_teachers,
            'has_org_fav':has_org_fav,
            'has_teacher_fav':has_teacher_fav

        })