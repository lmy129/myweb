from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    #定义用户模型
    mobile = models.CharField(verbose_name="手机号",max_length=11,unique=True)

    class Meta:
        verbose_name = "用户管理"
        verbose_name_plural = verbose_name
