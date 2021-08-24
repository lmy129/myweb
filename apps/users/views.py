from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import json
import re
from django.contrib.auth import login
# Create your views here.
class UsernameCountView(View):
    #定义检测用户名个数视图，防止用户名重复
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})

class MobileCountView(View):
    #定义检测手机号个数视图，防止手机号重复
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})


class RegisterView(View):
    #定义注册视图
    def post(self,request):
        #接收数据，前端传来的数据如果是查询字符串就在request.GET中，如果是表单数据就在request.POST中
        #如果是JSON或者XML就在request.body中
        body_data  = request.body
        #将上面接收到的json数据转换为字符串
        body_str = body_data.decode()
        #使用json的loads方法将字符串转换为字典，
        # json.loads可以将json数据转换为字典，json.dumps可以将字典转换为json
        body_dict = json.loads(body_str)

        #从字典中取出数据
        #这里使用字典的get方法而不是使用，body_dict[key]的方式是因为，get如果查询不到信息，不会报错
        #这样会使程序的健壮性更好
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        #获取是否同意协议的值，是一个bool类型
        allow = body_dict.get('allow')

        #使用if判断是否有为空的参数，这里all如果里面的内容有一个为空/None或者False那么就会返回False
        if not all([username,password,password2,mobile]):
            #返回一个响应，一般成功返回状态码0，失败返回400
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        #不要相信前端发来的任何信息，这里再做一次验证，防止有人使用脚本或者postman等软件进行注册
        if not re.match('[a-zA-Z0-9-_]{5,20}',username):
            #再次使用正则表达式验证用户名是否符合规则，不符合则返回400错误
            return JsonResponse({'code':400,'errmsg':'用户名不符合规则'})

        if len(password) < 8 and len(password) > 20:
            #判定密码长度不足8位或者大于20位则认为不符合规则
            return JsonResponse({'code':400,'errmsg':'密码不符合规则'})
        
        if password != password2:
            return JsonResponse({'code':400,'errmsg':'两次密码输入不一致'})

        if not re.match('1[345789]\d{9}',mobile):
            return JsonResponse({'code':400,'errmsg':'手机号错误'})

        '''
        这里不在验证allow，因为如果json数据传来的allow为false,那么在前面的all判断中就已经返回错误了
        '''

        '''
        这里使用User.objects.create_user()的方式添加用户到数据库是为了将password以加密的形式存储
        如果使用user = User();user = User.objects.create()的方式不会以加密形式存储password
        而是使用明文的方式保存密码
        '''
        user = User.objects.create_user(username=username,password=password,mobile=mobile)

        '''
        状态保持就是保持识别用户的登录状态，一般都是通过cookie和session来实现，将session保存到服务器里
        然后session也同时保存到cookie里发送给客户端保存，每当客户端访问的时候都在cookie里携带session信息
        发送到服务器，服务器进行比对确认，django同过中间件可以自动完成这些工作
        手动设置session信息：
        request.session['user_id'] = user.id
        '''
        #django提供的状态保持的方法通过login方法让用户登录
        login(request,user)

        return JsonResponse({'code':0,'errmsg':'ok'})
        


        
        

        



