# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

#Mixin函数结尾的都代表基础类
class LoginRequiredMixin(object):

    @method_decorator(login_required(login_url='/login/'))
    #函数名、参数固定
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)