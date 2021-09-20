from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.orders.models import OrderInfo
from utils.views import NewLoginRequiredMixin
from meiduo_mall import settings
from alipay import AliPay,AliPayConfig
import alipay

# Create your views here.
class PayUrlView(NewLoginRequiredMixin,View):
    def get(self,request,order_id):
        user = request.user

        try:
            #查询验证订单，订单要是未支付状态，并且是当前用户的订单
            order = OrderInfo.objects.get(pk=order_id,status=1,user=user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此订单'})

        #这里是设置美多商城应用的私钥和支付宝公钥
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        #创建支付实例
        alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调 url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2,具体参考支付宝支付设置
        debug=settings.ALIPAY_DEBYG,  # 默认 False
        verbose=False,  # 输出调试数据
        config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )

        subject = "测试订单"

        # 电脑网站支付，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string  这里是线上环境网址，若果是支付宝的沙箱则将alipay换成alipaydev
        #调用支付宝方法
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            #将金额类型转换为字符串
            total_amount=str(order.total_amount),
            subject=subject,
            #成功后跳转的地址
            return_url=settings.ALIPAY_RETURN_URL,
            notify_url="https://example.com/notify" # 可选，不填则使用默认 notify url
        )

        #拼接要跳转的链接
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string

        return JsonResponse({'code':0,'errmsg':'ok','alipay_url':pay_url})

        

