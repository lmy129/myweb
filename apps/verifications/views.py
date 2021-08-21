from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from django.http import HttpResponse
# Create your views here.
class ImagecodeView(View):
    #定义图片验证码视图
    def get(self,request,uuid):
        #使用generate_captcha()方法生成一个二进制图片和图片内容返回的是元组,text是图片验证码内容,image是二进制图片
        text,image=captcha.generate_captcha()
        #与redis取得链接并把验证码内容和uuid存到redis中的code别名库中【这个别名具体设置在settings.py中】
        redis_cli = get_redis_connection('code')
        #使用setex方法将接收到的uuid和生成的图片内容放到redis中，并且规定过期时间为100秒
        redis_cli.setex(uuid,100,text)
        #将生成的二进制图片放在响应中返还，这里注意二进制不能使用JSON传递所以没有使用JSONResponse
        #第二个参数content_type指定传输的是图片，这样在网页中显示不是乱码而是图片
        return HttpResponse(image,content_type='image/png')

    
