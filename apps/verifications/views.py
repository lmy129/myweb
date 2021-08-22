from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import View
#导入连接redis数据库方法
from django_redis import get_redis_connection
#导入生成图片验证码和图片二进制方法
from libs.captcha.captcha import captcha
from django.http import HttpResponse
#导入容联云发送短信验证码方法类
from libs.yuntongxun.sms import CCP
#导入random生成随机验证码
from random import randint


# Create your views here.
class ImagecodeView(View):
    #定义图片验证码视图
    def get(self,request,uuid):
        #使用generate_captcha()方法生成一个二进制图片和图片内容返回的是元组,text是图片验证码内容,image是二进制图片
        text,image=captcha.generate_captcha()
        #与redis取得链接并把验证码内容和uuid存到redis中的code别名库中【这个别名具体设置在settings.py中】
        redis_cli = get_redis_connection('code')
        #使用setex方法将接收到的uuid和生成的图片内容放到redis中，并且规定过期时间为100秒
        redis_cli.setex(uuid,300,text)
        #将生成的二进制图片放在响应中返还，这里注意二进制不能使用JSON传递所以没有使用JSONResponse
        #第二个参数content_type指定传输的是图片，这样在网页中显示不是乱码而是图片
        return HttpResponse(image,content_type='image/png')

class SmscodeView(View):
    #定义短信验证码视图
    def get(self,request,mobile):
        '''
        获取参数图片验证码内容,和uuid,这里图片验证码和对应的uuid是以查询字符串传递的，
        查询字符串内容在request.GET中【表单数据在request.POST中，JSON和XML数据在request.body中】
        '''
        image_text = request.GET.get('image_code').lower()
        image_id = request.GET.get('image_code_id')
        #验证参数是否齐全
        if not all([image_text,image_id]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        #连接redis中的'code'库
        redis_cli = get_redis_connection('code')
        #以接收到的image_id为key从code库中取出图片验证码内容
        redis_image_text = redis_cli.get(image_id)
        #将从reids中取出的base类型的图形验证码内容转码成字符串并转换成小写
        redis_image_text = redis_image_text.decode().lower()
        #验证图形验证码是否正确
        if redis_image_text == None:
            return JsonResponse({'code':400,'errmsg':'图片验证码过期'})
        if image_text != redis_image_text:
            return JsonResponse({'code':400,'errmsg':'验证码输入错误'})
        #生成验证码之前先检验用户是否频繁使用短信验证码
        send_flag = redis_cli.get('send_flag_%s' % mobile)
        if send_flag != None:
            return JsonResponse({'code':400,'errmsg':'请不要频繁使用短信验证码'})
        #生成随机六位数字验证码
        sms_code = '%06d' % randint(0,999999)
        '''
        将短线验证码放入redis中以备后面验证,这里以接收到的手机号为key
        是为了区分不同用户所分配的验证码方便验证
        '''
        redis_cli.setex(mobile,300,sms_code)
        #为了防止用户频繁的使用短信验证码，给当前已经申请发送验证码的手机号添加一个标记，持续60秒
        redis_cli.setex('send_flag_%s' % mobile,60,1)
        #发送短信验证码
        CCP().send_template_sms(mobile,[sms_code,6],1)
        #返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})
        




    
