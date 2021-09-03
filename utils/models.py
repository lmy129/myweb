from django.db import models

#定义一个用于所有模型继承的基类
class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间',auto_now=True)

    class Meta:
        #不让django给这个模型创建数据库表
        abstract = True