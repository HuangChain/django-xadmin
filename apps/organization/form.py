#encoding:utf-8

import re
from django import forms

from operation.models import UserAsk
from django.core.exceptions import ValidationError

class UserAskForm(forms.ModelForm):#多了model的属性，可直接进行save
    class Meta:
        model=UserAsk
        fields=['name','mobile','course_name']

    def clean_mobile(self):#语法：clean_＋字段名，对该字段进行规定、验证
        """
        正则表达式，验证手机号码是否合法
        """
        mobile=self.cleaned_data['mobile']#清除该字段，重新定义
        REGE_MOBILE='^1[138]\d{9}$|^147\d{8}$|^176\d{8}$'
        p=re.compile(REGE_MOBILE)
        if p.match(mobile):#如果匹配上
            return mobile
        else:
            s=forms.ValidationError(u'手机号码非法',code='moblie_invalid')
            # return s
            raise s
