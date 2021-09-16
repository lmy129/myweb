from django.db import models
from django.db.models.fields import related
from utils.models import BaseModel
from apps.users.models import Address, User
from apps.goods.models import SKU
# Create your models here.
class OrderInfo(BaseModel):
    '''订单信息'''
    #支付方式选项
    PAY_METHODS_ENUM = {
        'CASH':1,
        'ALIPAY':2,
    }
    PAY_METHOD_CHOICES = (
        (1,'货到付款'),
        (2,'支付宝'),
    )
    #订单状态码
    ORDER_STATUS_ENUM = {
        'UNPAID':1,
        'UNSEND':2,
        'UNRECEIVED':3,
        'UNCOMMENT':4,
        'FINISHED':5,
    }
    #订单状态选项
    ORDER_STATUS_CHOICES = (
        (1,'待支付'),
        (2,'代发货'),
        (3,'待收货'),
        (4,'待评价'),
        (5,'已完成'),
        (6,'已取消'),
    )
    #订单编号字段，设置该字段为订单表的主键【primary_key=True】代表该字段是不能为空并且是唯一的
    order_id = models.CharField(verbose_name='订单编号',primary_key=True,max_length=64)
    #与用户表关联，为一对多关系，并且当用户下有订单信息时不能删除该用户信息【on_delete=models.PROTECT】
    user = models.ForeignKey(User,on_delete=models.PROTECT,verbose_name='下单用户')
    #与地址表关联，为一对多关系，并且当有订单用到该地址信息是，不能删除该地址信息
    address = models.ForeignKey(Address,on_delete=models.PROTECT,verbose_name='收货地址')
    total_count = models.IntegerField(verbose_name='商品总数',default=1)
    #商品总金额字段，为金额字段，设置最大位数为10位【包含小数的位数】，并且小数位最多为2位
    total_amount = models.DecimalField(verbose_name='商品总金额',max_digits=10,decimal_places=2)
    freight = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='运费')
    pay_method = models.SmallIntegerField(verbose_name='支付方式',choices=PAY_METHOD_CHOICES,default=1)
    status = models.SmallIntegerField(verbose_name='订单状态',choices=ORDER_STATUS_CHOICES,default=1)

    class Meta:
        db_table = 'tb_order_info'
        verbose_name = '订单基本信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_id


class OrderGoods(BaseModel):
    '''订单商品'''
    SCORE_CHOICES = (
        (0,'0分'),
        (1,'20分'),
        (2,'40分'),
        (3,'60分'),
        (4,'80分'),
        (5,'100分'),
    )
    order = models.ForeignKey(OrderInfo,related_name='skus',on_delete=models.CASCADE,verbose_name='订单')
    sku = models.ForeignKey(SKU,on_delete=models.PROTECT,verbose_name='订单商品')
    count = models.IntegerField(verbose_name='数量',default=1)
    price = models.DecimalField(verbose_name='单价',max_digits=10,decimal_places=2)
    comment = models.TextField(verbose_name='评价信息',default='')
    score = models.SmallIntegerField(verbose_name='满意度评分',choices=SCORE_CHOICES,default=5)
    is_anonymous = models.BooleanField(verbose_name='是否匿名评价',default=False)
    is_commented = models.BooleanField(verbose_name='是否评价了',default=False)

    class Meta:
        db_table = 'tb_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name