from django.db import models

# Create your models here.
'''
这里是关于地址管理省市区应用，在这里将创建关于地址查询的模型。只创建一个表类似与这样
id  name    parent_id
100 河南省      null     #这里为null是因为省是最顶级没有上一级了
110 商丘市      100      #商丘上一级是河南所以parent_id为河南省的ID
120 洛阳市      100         
111 永城市      110      #永城上一级是商丘所以parent_id为商丘市的ID  
'''
class Area(models.Model):
    name = models.CharField(verbose_name='名称',max_length=20)
    '''
    parent参数详解：
    'self':虽然是一对多关联【一般一对多这里应该是一的模型名称】但是数据都在同一个模型同一个表中所以这里一的名称使用'self';
    on_delete=models.SET_NULL:删除关联数据【也就是一对多中的一】与之关联的数据设置为NULL，所以这里给parent设置了null=True;
    related_name='subs':重新设置查询方式【一对多通过一查询多时一般的格式为（一实例.多模型名称_set.all()）】这里related_name的
    作用就是重新定义查询方式为【一实例.subs.all()】
    null=True:设置在数据库中该字段可以为空值
    blank=True:设置填写表单时该字段可以为空
    '''
    parent = models.ForeignKey('self',
    on_delete=models.SET_NULL,
    related_name='subs',
    null=True,
    blank=True,
    verbose_name='上级行政区划')

    class Meta:
        #db_table设置在数据库中给该模型创建表时使用的名字
        db_table = 'db_areas'
        verbose_name = '省市区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
