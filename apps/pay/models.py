from typing import ByteString
from django.db import models
from apps.orders.models import OrderInfo
from utils.models import BaseModel
# Create your models here.
class Payment(BaseModel):
    '''支付信息'''
    order = models.ForeignKey(OrderInfo,on_delete=models.CASCADE,verbose_name='订单')
    trade_id = models.CharField(verbose_name='支付流水号',max_length=100,unique=True,null=True,blank=True)

    class Meta:
        db_table = 'tb_payment'
        verbose_name = '支付信息'
        verbose_name_plural = verbose_name