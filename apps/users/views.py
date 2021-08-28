from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import json
import re
from utils.views import NewLoginRequiredMixin
from django.contrib.auth import login,logout
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
        duo多账户功能实现，利用django内置的authenticate内置检测用户名和密码
        设置User.USERNAME_FIELD = '字段名' 设置根据什么字段作为用户名查询验证,先使用正则判断用户名输入的是不是手机号，如果是就设置手机号为用户名查询，如果不是就正常以用户名查询
        这里的User.USERNAME_FIELD = '字段名' 设置可以影响authenticate根据那个字段作为用户来查询
        '''
        if re.match('1[345789]\d{9}',username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

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

        '''
        在首页展示用户信息，有两种方式：1.通过请求获取用户信息在首页展示，2.在登录的时候将用户名信息添加到cookie里
        前端可以直接获取这个信息不用再重新请求一次，有利于性能的提高【这里使用第二种方式】
        增加cookie信息是用【set_cookie('名称',增加信息)】
        增加session信息是用【request.session('名称',session信息)】
        '''
        
        response = JsonResponse({'code':0,'errmsg':'ok'})
        #在返回响应中增加一个cookie信息，用户名,还可以添加一个max_age参数来设置cookie过期时间
        #如果不设置默认是浏览器关闭之后
        response.set_cookie('username',username)

        return response

class LogoutView(View):
    def delete(self,request):
        '''
        定义退出视图
        用户退出登录本质上是解除状态保持，也就是删除session信息
        然后这里因为我们前面在首页显示用户信息，使用的是在cooki中添加username信息的方法，
        所以还要再删除cookie中username的信息，否则再首页还会显示你好，用户名的显示
        '''
        logout(request)

        #删除cookie中的username信息
        response = JsonResponse({'code':0,'errmsg':'ok'})
        response.delete_cookie('username')

        #返回响应
        return response

class CenterView(NewLoginRequiredMixin,View):
    def get(self,request):

        info_data = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'ok','info_data':info_data})

class EmailView(NewLoginRequiredMixin,View):
    '''
    继承自NewLoginRequiredMixin和View两个类，继承NewLoginRequiredMixin是因为要使用其中的dispatch方法验证用户有没有登录
    【当前端有请求过来时，在路由中首先调用EmailView的as_view()方法这个时候按照MRO查找NewLoginRequiredMixin
    没有as_view()方法所以会到View中查找并且执行，然后调用dispatch方法还是首先从NewLoginRequiredMixin中查找之后执行验证用户
    是否登录，如果没有登录返回错误，如果登陆了则调用父类的dispatch方法由于其父类没有dispatch方法。所以会继续在View中查找dispatch
    方法，查找到后执行并且根据前端的请求类型交给对应的处理方法函数】

    定义保存验证邮箱视图,这里是更新用户信息，所以使用的是PUT请求
    字典使用get方法不会报错，但是如果访问数据库使用get当查询不到信息时会返回异常
    '''
    def put(self,request):

        #接收传输的email信息
        body_dict = json.loads(request.body.decode())

        #从字典中取出email
        email = body_dict.get('email')

        #通过正则匹配检查邮箱格式是否正确
        if not re.match('([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})',email):
            return JsonResponse({'code':400,'errmsg':'请输入正确的邮箱'})

        #获取当前登录用户信息
        user = request.user

        #更新用户信息
        user.email = email

        #保存用户信息
        user.save()

        return JsonResponse({'code':0,'errmsg':'ok'})





        


        
        

        



