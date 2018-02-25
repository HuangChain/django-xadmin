#encoding:utf-8
from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile

class LoginForm(forms.Form):
    username=forms.CharField(required=True)
    password=forms.CharField(required=True,min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True,error_messages={'required':u'邮箱不能为空'})
    password=forms.CharField(required=True,min_length=5)
    captcha = CaptchaField(error_messages={'required':u'验证码不能为空','invalid':u'验证码错误'})#自定义错误输出


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True,error_messages={'required':u'邮箱不能为空'})
    captcha = CaptchaField(error_messages={'required':u'验证码不能为空','invalid':u'验证码错误'})#自定义错误输出


class ModifyPwdForm(forms.Form):
    password = forms.CharField(required=True, min_length=5)
    confirm_password = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile #指明model
        fields = ['image']   #取model字段