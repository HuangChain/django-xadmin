# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import  make_password
from django.http import JsonResponse,HttpResponseRedirect
from pure_pagination import Paginator,PageNotAnInteger
from django.core.urlresolvers import reverse

from users.models import UserProfile,EmailVerify,Banner
from users.forms import LoginForm,RegisterForm,ForgetForm,ModifyPwdForm,UploadImageForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse,UserFavorite,UserMessage
from organization.models import CourseOrg,Teacher
from courses.models import Course
# Create your views here.

class CustomBackend(ModelBackend):
    def authenticate(self,username=None,password=None,**kwargs):
        try:
            user=UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class RegisterView(View):
    def get(self,request):
        register_form=RegisterForm()
        return render(request,'register.html',{'register_form':register_form})

    def post(self,request):
        register_form=RegisterForm(request.POST)
        if register_form.is_valid():
            email=request.POST.get('email')
            if UserProfile.objects.filter(email=email):
                return render(request,'register.html',{'register_form':register_form,'msg':u'用户已经存在!'})
            password=request.POST.get('password')
            user_profile=UserProfile()
            user_profile.username = email
            user_profile.email=email
            user_profile.password=make_password(password)
            user_profile.is_active=False
            user_profile.save()

            #写入欢迎注册消息
            user_message=UserMessage()
            user_message.user=user_profile
            user_message.message=u'欢迎注册慕学在线网'
            user_message.save()
            send_register_email(email,'register')
            return render(request,'login.html')
        else:
            print register_form
            return render(request,'register.html',{'register_form':register_form})


class ActiveUserView(View):
    def get(self,request,active_code):
        all_records=EmailVerify.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email=record.email
                user=UserProfile.objects.get(email=email)
                user.is_active=True
                user.save()
        else:
            return render(request,'active_fail.html')
        return render(request,"login.html")

class LogoutView(View):
    """
    用户退出
    """
    def get(self,request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))

class LoginView(View):
    def get(self,request):#重定义
        return render(request, 'login.html', {})

    def post(self,request):
        login_form=LoginForm(request.POST)#实例化
        if login_form.is_valid():
            user_name = request.POST.get('username', '')  # 默认值为空
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)#根据用户信息，login函数生成session_id,存储在数据库django_session表中
                    #return render(request, 'index.html')#登录过后直接render的话，会造成数据为空的情况
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': u'用户未激活!'})
            else:
                return render(request, 'login.html', {'msg': u'用户名或密码错误!'})
        else:
            print login_form.errors
            return render(request,'login.html',{'login_form':login_form})


# def user_login(request):
#     if request.method =='POST':
#         user_name=request.POST.get('username','')#默认值为空
#         pass_word=request.POST.get('password','')
#         user=authenticate(username=user_name,password=pass_word)
#         if user is not None:
#             login(request,user)
#             return render(request,'index.html')
#         else:
#             return render(request, 'login.html', {'msg':u'用户名或密码错误！'})
#
#     elif request.method == 'GET':
#         return render(request,'login.html',{})

class ForgetPwdView(View):
    def get(self,request):
        forget_form=ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form':forget_form})
    def post(self,request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email=request.POST.get('email')
            send_register_email(email,'forget')
            return render(request,'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView1(View):
    def get(self,request,reset_code):
        all_records=EmailVerify.objects.filter(code=reset_code)
        if all_records:
            for record in all_records:
                email=record.email
                return render(request,'password_reset.html',{'email':email})
        else:
            return render(request,'active_fail.html')
        return render(request,"login.html")

class ResetView2(View):
    def post(self,request):
        modify_form=ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            email=request.POST.get('email')
            password=request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password != confirm_password:
                return render(request,'password_reset.html',{'email':email,'msg':u'密码不一致，请重新输入！'})
            else:
                password=make_password(password)
                user= UserProfile.objects.get(email=email)
                user.password=password
                user.save()
                return render(request,'login.html')
        else:
            email = request.POST.get('email')
            return render(request,'password_reset.html',{'email':email,'modify_form':modify_form})

class UserinfoView(LoginRequiredMixin,View):
    """
    用户个人信息
    """
    def get(self,request):
        return render(request,'usercenter-info.html',{

        })


class UploadImageView(LoginRequiredMixin,View):
    """
    用户修改头像
    """
    def post(self,request):
        image_form=UploadImageForm(request.POST,request.FILES,instance=request.user)#文件放在request.FILES，将用户上传文件保存到form
                                                                                    #instance=request.user使其既有form又有model的特性
        # if image_form.is_valid():
        #     image=image_form.cleaned_data['image']#form验证通过的字段全放到cleaned_data变量，故可通过该变量取出字段
        #     request.user.image=image
        #     request.user.save()
        #     pass
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail'})


class UpdatePwdView(View):
    def post(self,request):
        modify_form=ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            password=request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password != confirm_password:
                return JsonResponse({'status': 'fail','msg':u'密码不一致'})
            user = request.user
            password=make_password(password)
            user.save()
            return JsonResponse({'status': 'success'})#返回json标准的字符串
        else:
            return JsonResponse(modify_form.errors)#参数是字典


class SendEmailCodeView(LoginRequiredMixin,View):
    def get(self,request):
        email=request.GET.get('email','')
        if UserProfile.objects.filter(email=email):
            return JsonResponse({'email':u'邮箱已经存在'})
        send_register_email(email,'update_email')
        return JsonResponse({'email': u'发送成功'})

class MyCourseView(LoginRequiredMixin,View):
    """
    我的课程
    """
    def get(self,request):
        user_courses=UserCourse.objects.filter(user=request.user)
        return render(request,'usercenter-mycourse.html',{
            'user_courses': user_courses
        })


class MyFavOrgView(LoginRequiredMixin,View):
    """
    我收藏的课程机构
    """
    def get(self,request):
        org_list=[]
        fav_orgs=UserFavorite.objects.filter(user=request.user,fav_type='2')
        for fav_org in fav_orgs:
            org_id=fav_org.fav_id
            org=CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request,'usercenter-fav-org.html',{
            'fav_orgs': fav_orgs,
            'org_list':org_list
        })

class MyFavTeacherView(LoginRequiredMixin,View):
    """
    我收藏的授课讲师
    """
    def get(self,request):
        teacher_list=[]
        fav_teachers=UserFavorite.objects.filter(user=request.user,fav_type='3')
        for fav_teacher in fav_teachers:
            teacher_id=fav_teacher.fav_id
            teacher=Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request,'usercenter-fav-teacher.html',{
            'teacher_list': teacher_list,
        })

class MyFavCourseView(LoginRequiredMixin,View):
    """
    我收藏的课程
    """
    def get(self,request):
        course_list=[]
        fav_courses=UserFavorite.objects.filter(user=request.user,fav_type='3')
        for fav_course in fav_courses:
            course_id=fav_course.fav_id
            course=Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request,'usercenter-fav-course.html',{
            'course_list': course_list,
        })

class MymessageView(LoginRequiredMixin,View):
    """
    我的消息
    """
    def get(self,request):
        all_messages=UserMessage.objects.filter(user=request.user.id)

        #用户进入个人消息后清空未读消息的记录
        all_unread_messages=UserMessage.objects.filter(user=request.user.id,has_read=False)
        for unread_messages in all_unread_messages:
            unread_messages.has_read=True
            unread_messages.save()
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_messages, 3, request=request)  # 对all_org进行分页,每页5条数据
        messages = p.page(page)  # 取第page页的数据,不是一个query_set类，故前端访问变量时需加上.object_list
        return render(request,'usercenter-message.html',{
            'messages':messages
        })

class IndexView(View):
    #慕学在线网首页
    def get(self,request):
        all_banners=Banner.objects.all().order_by('index')
        courses =Course.objects.filter(is_banner=False)[:6]
        banner_courses=Course.objects.filter(is_banner=True)[:3]
        course_org=CourseOrg.objects.all()[:15]
        return render(request,'index.html',{
            'all_banners':all_banners,
            'courses':courses,
            'banner_courses':banner_courses,
            'course_org':course_org
        })


def page_not_found(request):
    #全局404处理函数
    from django.shortcuts import render_to_response
    response =render_to_response('404.html',{})
    response.status_code=404#返回状态码
    return response

def page_error(request):
    #全局500处理函数
    from django.shortcuts import render_to_response
    response =render_to_response('500.html',{})
    response.status_code=500
    return response

# class LoginUnSafeView(View):
#     def get(self,request):
#         return render(request,'login.html',{})
#     def post(self,request):
#         user_name = request.POST.get('username', '')
#         pass_word = request.POST.get('password', '')
#
#         import MySQLdb #python连接mysql驱动
#         conn= MySQLdb.connect(
#             host='127.0.0.1',
#             user='root',
#             passwd='password',
#             db='mxonline',
#             charset='utf8' #指明连接数据集
#         )#建立mysql联系
#         cursor=conn.cursor()
#         sql_select='select * from users_userprofile where email= "{0}" and password="{1}"'.format(user_name,pass_word)
#         result=cursor.execute(sql_select)#执行sql
#         for row in cursor.fetchall():#该函数可以取到查询出来的所有语句
#             #查询到用户
#             pass