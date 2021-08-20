from django.shortcuts import render
from django.views import View
from .models import User
from django.http import JsonResponse
import re
import json
from django.contrib.auth import login

# Create your views here.
class UsernameCountView(View):
    #定义检查用户名个数视图
    def get(self,request,username):
        #django接收URL路径中的参数使用尖括号，如果没有过滤器【例如<int:id>】则接收除'/'外的所有字符
        #if re.match('[a-zA-Z0-9_-]{5,20}',username): [因为使用了自定义的转换器所以视图中不再使用条件判断]
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})
        #else:
            #return JsonResponse({'code':200,'errmsg':'用户名不满足需求'})

class UsermobileCountView(View):
    #定义检查手机号个数视图
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})

class RegisterView(View):
    #定义注册视图
    def post(self,request):
        #从request.body中接收数据，是一个json数据[表单数据用request.post接收，非表单数据用body]
        body_data = request.body
        #将接收到的数据转换未字符串
        body_str = body_data.decode()
        #将字符串转换未字典
        body_dict = json.loads(body_str)

        #使用字典的get方法，不使用body_dict['username']的方式是因为,get查询不到不报错，提高程序的健壮性
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        #这里获取的是是否同意协议的值
        allow = body_dict.get('allow')

        #验证上面获取到的数据又没有空值也就是None如果有就返回错误消息
        if not all([username,password,password2,mobile,allow]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        #验证用户名是否符合规则
        if not re.match('[a-zA-Z0-9_-]{5,20}',username):
            return JsonResponse({'code':400,'errmsg':'用户名不符合规则'})
        if len(password) < 8 or len(password) > 20 :
            return JsonResponse({'code':400,'errmsg':'密码不符合规则'})
        if password != password2:
            return JsonResponse({'code':400,'errmsg':'两次输入密码不一致'})
        if not re.match('^1[345789]\d{9}$',mobile):
            return JsonResponse({'code':400,'errmsg':'手机号有误'})
        '''这里不再验证allow因为allow是是否同意协议的值，如果JSON传进来是false转换后是False在上面的all判断中就会返回错误
        #如果JSON传进来时true，转换后就是True也就是同意用户协议'''
        #if not allow:
            #return JsonResponse({'code':400,'errmsg':'没有同意用户协议'})
        
        #使用这种方式可以使密码加密;并赋值给user用以登录
        user = User.objects.create_user(username=username,password=password,mobile=mobile)

        #这种方式保存到数据库密码不会加密
        #User.objects.create(username=username,password=password,mobile=mobile)
        #user = User(username=username,password=password,mobile=mobile)
        #user.save()

        #登录[状态保持：给客户端保存cookie服务器使用session]
        login(request,user)
        return JsonResponse({'code':0,'errmsg':'ok'})




