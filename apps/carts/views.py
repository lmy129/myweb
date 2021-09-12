from django.shortcuts import render
from django.views import View
import json
from apps.goods.models import SKU
from django.http import JsonResponse
from django_redis import get_redis_connection
import pickle
import base64

# Create your views here.
def CartsView(View):
    '''购物车视图，采取登录用户和不登录用户都可使用购物车功能方案
    登录用户的购物车数据保存在redis中【哈希结构】
    不登录用户的购物车数据保存在cookie中【字典结构，但是使用base64进行重新编码】'''
    def post(self,request):
        #接收参数
        data = json.loads(request.body.decode())
        #获取商品id和用户id数据,商品数量数据,并且进行验证
        sku_id = data.get('sku_id')
        count = data.get('sku_id')
        #验证商品id是否正确
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})
        #验证商品数量是否为整数，进行强制转换，如果出现异常则将数量设为1
        try:
            count = int(count)
        except Exception:
            count = 1

        user = request.user
        #判断用户是否登录
        if user.is_authenticated:
            #链接到redis
            redis_cli = get_redis_connection('carts')
            #用哈希表保存商品id和数量
            redis_cli.hset('carts_%s' % user.id,sku.id,count)
            #用集合保存商品id用于判断是否打钩选中
            redis_cli.sadd('selected_%s' % user.id,sku.id)
        else:
            #从请求cookie中获取购物车数据
            cookie_carts = request.COOKIES.get('carts')
            #判断cookie_carts中有没有数据
            if cookie_carts:
                #对加密数据进行解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                #初始化一个空字典
                carts = {}
            #判断添加的商品ID是否已经存在购物车数据中
            if sku_id in carts:
                #读取原有购物车中的商品数量
                origin_count = carts[sku_id]['count']
                #更新商品数据
                count += origin_count
            #更新购物车数据
            carts[sku_id] = {
                'count':count,
                'selected':True,
            }

            #将数据转换为二进制的数据
            carts_bytes = pickle.dumps(carts)
            #将二进制数据重新编码为base64编码
            carts_bytes_base64 = base64.b64encode(carts_bytes)
            #将改变编码后的数据转换为字符串
            carts_bytes_base64_str = carts_bytes_base64.decode()
            #设置cookie
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('carts',carts_bytes_base64_str,max_age=3600*24*12)
            #返回响应
            return response

    def get(self,request):
        #展示购物车数据
        user = request.user
        #判断用户是否登录
        if user.is_anthenticated:
            #登录用户查询redis
            redis_cli = get_redis_connection('carts')
            #获取商品ID和数量数据
            sku_id_count = redis_cli.hgetall('carts_%s' % user.id)
            #获取商品是否选中状态
            selected_ids = redis_cli.smembers('selected_%s' % user.id)

            #将登录用户的购物车数据转换成与未登录用户购物车数据一致，便于最后重复使用代码
            #初始化一个字典
            carts = {}
            #遍历商品ID和数量，将数据添加到字典中
            for sku_id,count in sku_id_count.items():
                carts[sku_id]={
                    'count':count,
                    'selected':sku_id in selected_ids,
                }
        else:
            #获取购物车数据
            cookie_carts = request.COOKIE.get('carts')
            #判断有没有cookie数据
            if cookie_carts != None:
                #将购物车数据进行解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                #初始化一个空字典，这里是为了后面的公共代码不出错
                carts = {}

        #从字典中取出所有的商品ID
        sku_ids = carts.keys()
        #根据商品ID查询对应的商品
        skus = SKU.objects.filter(id__in=sku_ids)
        #对查询到的结果集进行遍历,将数据转换为字典形式
        skus_list = []
        for sku in skus:
            skus_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image_url,
                'price':sku.price,
                'count':carts[sku_id]['count'],
                'selected':carts[sku_id]['selected'],
                'amount':sku.price * carts[sku_id]['count'],
            })
        return JsonResponse({'code':0,'errmsg':'ok','carts_skus':skus_list})


