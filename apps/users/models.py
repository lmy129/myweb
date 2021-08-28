from django.db import models
#导入django内置的用户类，在这个用户类的基础上去拓展用户模型
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    #定义User类

    #在原有的用户类AbstractUser基础上拓展一个mobile字段用于存放用户手机号
    mobile = models.CharField(verbose_name='手机号',max_length=11,unique=True)
    #拓展一个记录验证邮箱状态的布尔型字段
    email_active = models.BooleanField(verbose_name='邮箱验证状态',default=False)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
