from django.db import models
#导入django内置的用户类，在这个用户类的基础上去拓展用户模型
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import PROTECT
# Create your models here.

class User(AbstractUser):
    #定义User类

    #在原有的用户类AbstractUser基础上拓展一个mobile字段用于存放用户手机号
    mobile = models.CharField(verbose_name='手机号',max_length=11,unique=True)
    #拓展一个记录验证邮箱状态的布尔型字段
    email_active = models.BooleanField(verbose_name='邮箱验证状态',default=False)
    #给用户一个默认地址字段与地址模型对应，这样做是为了在关于地址的数据表中少一个字段，进行优化
    default_address = models.ForeignKey('Address',related_name='users',null=True,blank=True,on_delete=models.SET_NULL,verbose_name='默认地址')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class Address(models.Model):
    #定义用户收货地址模型

    #收货地址与用户是一对多关系，并且是级联删除，定义当使用一(用户)进行查询时，使用user实例.addresses.all()的方式查询
    #原来是user实例.address_set.all()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses',verbose_name='用户')
    #地址的别名也就是每个收货地址的命名
    title = models.CharField(verbose_name='地址名称',max_length=20)
    #收货人
    receiver = models.CharField(verbose_name='收货人',max_length=20)
    #这里的on_delete=PROTECT意思是当删除关联的一数据时会引发ProtectedError来阻止删除【因为它已经被关联起来了】
    province = models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='province_addresses',verbose_name='省份')
    city = models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='city_addresses',verbose_name='城市')
    district = models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='district_addresses',verbose_name='区县')
    place = models.CharField(max_length=50,verbose_name='地址')
    mobile = models.CharField(max_length=11,verbose_name='手机')
    #定义固定电话在数据库中可以为null值(查询出来是None)，blank=True填写表单是可以为空，默认为空
    tel = models.CharField(max_length=20,null=True,blank=True,default='',verbose_name='固定电话')
    email = models.CharField(max_length=30,null=True,blank=True,default='',verbose_name='邮箱')
    is_deleted = models.BooleanField(default=False,verbose_name='逻辑删除')
    #定义创建时间和更新时间，auto_now_add指的是在创建的时候会使用当前时间，在修改等操作中这个时间不变
    #auto_now指的是在创建/修改等所有操作中都将改变时间为现在的时间
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间',auto_now=True)

    class Mate:
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        #定义查询排序时使用倒序，也就是后添加的在上
        ordering = ['-update_time']


