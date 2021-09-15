from django.http.response import JsonResponse
from django.shortcuts import render
from utils.views import NewLoginRequiredMixin
from django.views import View
from apps.users.models import Address
from apps.goods.models import SKU
from django_redis import get_redis_connection
# Create your views here.
'''
订单页面
'''
class OrderSettlementView(NewLoginRequiredMixin,View):
    def get(self,request):
        #获取用户信息
        user = request.user
        #查询用户地址信息
        addresses = user.addresses.filter(is_deleted=False)
        #将地址对象数据转换为字典数据
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id':address.id,
                'province':address.province.name,
                'city':address.city.name,
                'district':address.district.name,
                'place':address.place,
                'receiver':address.receiver,
                'mobile':address.mobile,
            })
        #链接redis
        redis_cli = get_redis_connection('carts')
        #创建查询数据的管道
        pipeline = redis_cli.pipeline()
        pipeline.hgetall('carts_%s' % user.id)
        pipeline.smembers('selected_%s' % user.id)
        #接收管道查询的数据，是一个列表，第一个查询的在第一个
        result = pipeline.execute()
        #接收管道查询列表中的数据
        sku_id_counts = result[0]
        selected_ids = result[1]
        #重新组织一个选中的信息
        selected_carts = {}
        for sku_id in selected_ids:
            selected_carts[int(sku_id)] = int(sku_id_counts[sku_id])

        #查询商品数据
        skus_list = []
        for sku_id,count in selected_carts.items():
            sku = SKU.objects.get(pk=sku_id)
            skus_list.append({
                'id':sku.id,
                'count':count,
                'name':sku.name,
                'price':sku.price,

            })
        return JsonResponse({'code':0,'errmsg':'ok','addresses':addresses_list,'skus_list':skus_list})
        

