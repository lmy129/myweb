from apps.orders.models import OrderInfo,OrderGoods
from django.http.response import JsonResponse
from django.shortcuts import render
from utils.views import NewLoginRequiredMixin
from django.views import View
from apps.users.models import Address
from apps.goods.models import SKU
from django_redis import get_redis_connection
import json
from django.utils import timezone
#导入用于金额的类
from decimal import Decimal
from django_redis import get_redis_connection
#导入事务模块
from django.db import transaction
from time import sleep
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
        
class OrderCommitView(NewLoginRequiredMixin,View):
    '''提交订单--生成订单视图'''
    def post(self,request):
        user = request.user
        #接收请求数据
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        #验证数据
        if not all([address_id,pay_method]):
            return  JsonResponse({'code':0,'errmsg':'参数不全'})
        
        try:
            address=Address.objects.get(pk=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数不正确'})
        
        #判断选择的支付方式1为现金，2为支付宝
        if pay_method not in [1,2]:
            return JsonResponse({'code':400,'errmsg':'参数不正确'})

        #生成订单编号,也就是订单表的主键，这个表的主键是自己定义的，因为模型中order_id字段设置了【primary_key=True】
        #这里使用了'%Y%m%d%H%M%S'将时间格式化获得类似20210915093625的数据，‘%09d’也是将用户ID格式化强制为9位不够的左边补0，例如用户ID为3则获得000000003
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        #根据支付方式设置订单的支付状态
        if pay_method == 1:
            #支付方式是现金，设置订单状态为待发货
            status = 2
        else:
            #支付方式是支付宝，设置订单状态为待支付
            status = 1

        #订单总数量和总金额设置为0，是为了在后面遍历查询商品表时再更新，节省服务器资源
        total_count = 0
        #商品总金额
        total_amount = Decimal('0')
        #设置运费
        freight = Decimal('10.00')
        #创建订单,用一个变量接收方便下面使用

        #使用事务控制订单的创建和商品库存的改变
        with transaction.atomic():
            #创建一个开始点，如果失败的话会回滚到开始点的状态
            point = transaction.savepoint()
            orderinfo = OrderInfo.objects.create(
                order_id = order_id,
                user = user,
                address = address,
                total_count = total_count,
                total_amount = total_amount,
                freight = freight,
                pay_method = pay_method,
                status = status
            )

            #商品数据部分
            redis_cli = get_redis_connection('carts')
            pipeline = redis_cli.pipeline()
            #接收商品ID和商品数量数据
            pipeline.hgetall('carts_%s' % user.id)
            #接收商品选中信息数据
            pipeline.smembers('carts_%s' % user.id)
            #使用一个变量接收管道查询到的信息
            result = pipeline.execute
            sku_id_count = result[0]
            selected_id = result[1]

            #重新组织一个数据
            carts = {}
            for sku_id in selected_id:
                #强制转换为整型，方便判断库存
                carts[int(sku_id)] = int(sku_id_count[sku_id])

            #查询单个商品信息
            for sku_id,count in carts.items():
                #for i in range(10)重复10次
                while True:
                    #try:   在事务中不使用try错误捕获，以免出现意料之外的操作
                    sku = SKU.objects.get(pk=sku_id)
                    #except SKU.DoesNotExist:
                    #return JsonResponse({'code':400,'errmsg':'没有此商品'})
                    
                    if sku.stock < count:
                        #创建一个回滚点，判断库存是否充足，如果库存不足回滚到开始点
                        #transaction.savepoint_rollback(point)
                        #return JsonResponse({'code':400,'errmsg':'库存不足'})
                        sleep(0.005)
                        continue
                    '''#调整库存
                    sku.stock -= count
                    #调整销量
                    sku.sales += count
                    sku.save()
                    使用乐观锁解决超卖问题
                    '''
                    #先保存一个库存数据
                    old_stock = sku.stock
                    #使用一个变量接收要更新的数据
                    new_stock = sku.stock - count
                    new_sales = sku.sales + count
                    #判断能不能更新数据,当前商品查询到的库存要与保存的库存数据一致才可以操作数据【证明没有人在操作这个数据】
                    result = SKU.objects.filter(pk=sku.id,stock=old_stock).update(stock=new_stock,sales=new_sales)
                    #当更新成功时result为1，不成功则result为0
                    if result == 0:
                        #回滚事务到开始点
                        transaction.get_rollback(point)
                        return JsonResponse({'code':400,'errmsg':'下单失败'})
                    orderinfo.total_count += count
                    orderinfo.total_amount += (count * sku.price)

                    OrderGoods.objects.create(
                        order = orderinfo,
                        sku = sku,
                        count = count,
                        price = sku.price
                    )
                    break
            orderinfo.save()
            #提交点，如果整个过程没有问题，则会提交修改，这里可以省略因为with语句会自动提交
            transaction.savepoint_commit(point)
        return JsonResponse({'code':0,'errmsg':'ok','order_id':order_id})





        
        
