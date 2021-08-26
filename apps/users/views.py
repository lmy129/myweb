from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import json
import re
from django.contrib.auth import login
#django内置的验证用户名密码方法
from django.contrib.auth import authenticate
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

class LoginView(View):
    #定义登录视图
    '''
    这里虽然不是新增数据但是还是用post请求，是因为如果使用get请求则用户名密码会作为查询参数直接明文暴露在路由里不安全。
    查询数据使用get请求，新增数据使用post请求，更新使用put请求，删除使用delete请求
    '''
    def post(self,request):
        '''
        接收参数，如果前端给的是表单数据则数据在request.POST中，这里前端给的是JSON数据数据在request.body中
        从JSON中取出数据一般步骤：
        1. body_data = request.body 将body中的数据赋值给body_data,此时是一个base类型数据
        2. body_str = body_data.decode() 将body_data中的base数据转换成字符串
        3. body_dict = json.loads(body_str) 将字符串数据转换为字典
        这里直接将上面三步写在一起
        '''
        now_user = json.loads(request.body.decode())

        #从now_user中取出username和password
        username = now_user.get('username')
        password = now_user.get('password')
        remembered = now_user.get('remembered')


        #验证用户名和密码是否为空如果有空值则返回400给前端
        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        '''
        参数齐全开始验证用户名密码如果通过验证则执行登录实现状态保持
        user = User.objects.get(username=username)
        if not username:
            return JsonResponse({'code':400,'errmsg':'没有该用户'})
        if password == user.password:
            login(request,user)
        这里使用django自带的验证用户名密码模块authenticate,传入用户名和密码如果验证成功则返回User对象如果验证不成功则返回None
        '''
        user = authenticate(username=username,password=password)
        if user == None:
            return JsonResponse({'code':400,'errmsg':'用户名或密码错误'})
        login(request,user)

        '''
        如果用户选择记住选项【这里不是记住用户名密码是记住登录状态下次登录免登陆，而记住用户名密码是下次登录直接自动填充用户名密码在登录页】
        使用request.session.set_expiry(value)
        如果参数value为1个整数则session会在value秒后过期，如果value为None则session会在两周后过期，如果value为0则session会在浏览器关闭后过期
        可以通过settings.py中通过SESSION_COOKIE_AGE来设置全局默认值
        '''
        if remembered != True:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        
        return JsonResponse({'code':0,'errmsg':'ok'})

        


        
        

        



