from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from libs.captcha.captcha import captcha
from django.views import View
from django_redis import get_redis_connection
from random import randint
from libs.yuntongxun.sms import CCP
# Create your views here.

class ImageCodeView(View):
    def get(self,request,uuid):
        #使用generate_captcha()方法生成一个二进制图片和图片内容返回的是元组,
        # text是图片验证码内容,image是二进制图片
        text,image = captcha.generate_captcha()

        #建立与redis的链接,链接到别名code的2号库
        redis_cli = get_redis_connection('code')

        #将uuid和图片验证码的内容存入redis
        #使用setex方法可以指定数据有效时间，这里以uuid为key以text为值，设定有效时间为300秒
        redis_cli.setex(uuid,300,text)

        #将生成的二进制图片放在响应中返还，这里注意二进制不能使用JSON传递所以没有使用JSONResponse
        #第二个参数content_type指定传输的是图片，这样在网页中显示不是乱码而是图片
        return HttpResponse(image,content_type='image/jpeg')

class SmsCodeView(View):
    #定义发送短信验证码视图
    def get(self,request,mobile):
        '''
        这里首先接收图片验证码和uuid并且与redis中的数据进行比对，验证通过才能发送短信验证码，
        这样做是为了防止用户通过脚本等工具频繁发送短信
        图片验证码和uuid在查询字符串中进行传输
        查询字符串内容在request.GET中【表单数据在request.POST中，JSON和XML数据在request.body中】
        '''
        image_text = request.GET.get('image_code').lower()
        image_id = request.GET.get('image_code_id')

        #验证图片验证码和uuid的数据有效行
        if not all([image_text,image_id]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        #链接redis数据库
        redis_cli = get_redis_connection('code')
        #从redis数据库中取出相应的图片验证码,取出的是base数据
        redis_image_text = redis_cli.get(image_id)
        #将base类型的数据转换成字符串，并且转换成小写
        redis_image_text = redis_image_text.decode().lower()

        #首先判断图形验证码是否过期
        if redis_image_text == None:
            return JsonResponse({'code':400,'errmsg':'图片验证码过期'})
        #验证图形验证码是否正确
        if image_text != redis_image_text:
            return JsonResponse({'code':400,'errmsg':'图片验证码输入错误'})

        #验证是否是频繁操作
        send_flag = redis_cli.get('send_flag_%s' % mobile)
        if send_flag != None:
            return JsonResponse({'code':400,'errmsg':'请不要频繁发送短信验证码'})

        #验证无误生成短信验证码
        sms_code = '%06d' % randint(0,999999)

        '''
        将短信验证码放入redis中以备后面验证,这里以接收到的手机号为key
        是为了区分不同用户所分配的验证码方便验证
        这里还可以使用管道来减少python客户端与redis的交互次数来提高性能：
        1.创建一个管道
        pipline = redis_cli.pipeline()
        2.使用管道收集指令
        pipline.setex(mobile,300,sms_code)
        pipline.setex('send_flag_%s' % mobile,60,1)
        3.执行指令[将收集到的指令一次全写进redis数据库，减少与数据库的连接次数]
        pipeline.execute()
        '''
        #将短信验证码存入redis数据库,有效期300秒
        redis_cli.setex(mobile,300,sms_code)

        #发送短信验证码之前存入一个标记，防止用户频繁使用短信验证码
        redis_cli.setex('send_flag_%s' % mobile,60,1)

        #发送短信验证码
        CCP().send_template_sms(mobile,[sms_code,6],1)

        #返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})


        

        

