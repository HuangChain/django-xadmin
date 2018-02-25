#encoding:utf-8
from random import Random
from django.core.mail import send_mail

from users.models import EmailVerify
from MxOnline.settings import DEFAULT_FROM_EMAIL

def random_str(randomlength=8):
    str=''
    chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNn'
    length=len(chars)-1
    random=Random()
    for i in range(randomlength):#range(5),代表从0到5(不包含5);range(1,5)代表从1到5(不包含5);range(1,5,2)代表从1到5，间隔2(不包含5)
        str+=chars[random.randint(0,length)]#用于生成一个指定范围内的整数。生成的随机数n: a <= n <= b
    return str


def send_register_email(email,send_type1='register'):
    email_verify=EmailVerify()
    if send_type1 == 'update_email':
        code = random_str(4)
    else:
        code=random_str(16)
    email_verify.code=code
    email_verify.email=email
    email_verify.send_type=send_type1
    email_verify.save()
    if send_type1=='register':
        email_title=u"慕学在线网注册激活链接"
        email_body=u'请点击下面的链接激活你的账号：http://127.0.0.1/8000/active/{}'.format(code)
        send_status=send_mail(email_title,email_body,DEFAULT_FROM_EMAIL,[email])
        if send_status:
            pass
    elif send_type1=='forget':
        email_title=u"慕学在线网注册密码重置链接"
        email_body=u'请点击下面的链接重置密码：http://127.0.0.1/8000/reset/{0}'.format(code)
        send_status=send_mail(email_title,email_body,DEFAULT_FROM_EMAIL,[email])
        if send_status:
            pass

    elif send_type1=='update_email':
        email_title=u"慕学在线网邮箱修改验证码"
        email_body=u'你的邮箱验证码为:{0}'.format(code)
        send_status=send_mail(email_title,email_body,DEFAULT_FROM_EMAIL,[email])
        if send_status:
            pass