from django.db import models
from django.db.models.fields import BooleanField
from utils.models import BaseModel
#富文本编辑器，使用ckeditor中的字段可以直接代替django内置的models.TextField字段使用
#from ckeditor.fields import RichTextField
#from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class GoodsCategory(BaseModel):
    '''商品类别'''
    name=models.CharField(verbose_name='名称',max_length=10)
    parent = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,verbose_name='父类别')

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsChannel(BaseModel):
    '''商品频道'''
    group_id = models.IntegerField(verbose_name='组号')
    category = models.ForeignKey(GoodsCategory,on_delete=models.CASCADE,verbose_name='顶级商品类别')
    url = models.CharField(verbose_name='频道页面链接',max_length=50)
    sequence = models.IntegerField(verbose_name='组内顺序')

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = '商品频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name

class Brand(BaseModel):
    '''品牌'''
    name = models.CharField(verbose_name='名称',max_length=20)
    logo = models.ImageField(verbose_name='logo图片')
    first_letter = models.CharField(verbose_name='品牌首字母',max_length=1)

    class Meta:
        db_table = 'tb_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Goods(BaseModel):
    '''商品SPU'''
    name = models.CharField(verbose_name='名称',max_length=50)
    brand = models.ForeignKey(Brand,on_delete=models.PROTECT,verbose_name='品牌')
    category1 = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,related_name='cat1_goods',verbose_name='一级类别')
    category2 = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,related_name='cat2_goods',verbose_name='二级类别')
    category3 = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,related_name='cat3_goods',verbose_name='三级类别')
    sales = models.IntegerField(verbose_name='销量',default=0)
    comments = models.IntegerField(verbose_name='评价数',default=0)
    #RichTextUploadingField是一个可以放图片的富文本字段
    #desc_detail = RichTextUploadingField(verbose_name='详细介绍',default='')
    #desc_pack = RichTextField(verbose_name='包装信息',default='')
    #desc_service = RichTextUploadingField(verbose_name='售后服务')
    desc_detail = models.TextField(verbose_name='详细介绍',default='')
    desc_pack = models.TextField(verbose_name='包装信息',default='')
    desc_service = models.TextField(verbose_name='售后服务',default='')
    class Meta:
        db_table = 'tb_goods'
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsSpecification(BaseModel):
    '''商品规格'''
    goods = models.ForeignKey(Goods,on_delete=models.CASCADE,verbose_name='商品')
    name = models.CharField(verbose_name='规格名称',max_length=20)

    class Meta:
        db_table = 'tb_goods_specification'
        verbose_name = '商品规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class SpecificationOption(BaseModel):
    '''规格选项'''
    spec = models.ForeignKey(GoodsSpecification,on_delete=models.CASCADE,verbose_name='规格')
    value = models.CharField(max_length=20,verbose_name='选项值')

    class Meta:
        db_table = 'tb_specification_option'
        verbose_name = '规格选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.spec,self.value)

class SKU(BaseModel):
    '''商品SKU'''
    name = models.CharField(verbose_name='名称',max_length=50)
    caption = models.CharField(verbose_name='副标题',max_length=100)
    goods = models.ForeignKey(Goods,on_delete=models.CASCADE,verbose_name='商品')
    category = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,verbose_name='从属类别')
    #价格定义为一个固定精度的十进制数字段，规定最大位数为10，小数位数为2
    price = models.DecimalField(verbose_name='单价',max_digits=10,decimal_places=2)
    cost_price = models.DecimalField(verbose_name='进价',max_digits=10,decimal_places=2)
    market_price = models.DecimalField(verbose_name='市场价',max_digits=10,decimal_places=2)
    stock = models.IntegerField(verbose_name='库存',default=0)
    sales = models.IntegerField(verbose_name='销量',default=0)
    comments = models.IntegerField(verbose_name='评价数',default=0)
    is_launched = models.BooleanField(verbose_name='是否上架销售',default=True)
    default_image_url = models.CharField(verbose_name='默认图片',max_length=200,default='',null=True,blank=True)

    class Meta:
        db_table = 'tb_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id,self.name)

class SKUImage(BaseModel):
    '''SKU图片'''
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,verbose_name='sku')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.name,self.id)

class SKUSpecification(BaseModel):
    '''SKU具体规格'''
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,verbose_name='sku')
    spec = models.ForeignKey(GoodsSpecification,on_delete=models.PROTECT,verbose_name='规格名称')
    option = models.ForeignKey(SpecificationOption,on_delete=models.PROTECT,verbose_name='规格值')

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'SKU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s - %s' % (self.sku,self.spec.name,self.option.value)

class GoodsVisitCount(BaseModel):
    '''统计分类商品访问量模型类'''
    category = models.ForeignKey(GoodsCategory,on_delete=models.CASCADE,verbose_name='商品分类')
    count = models.IntegerField(verbose_name='访问量',default=0)
    date = models.DateField(auto_now_add=True,verbose_name='统计日期')

    class Meta:
        db_table = 'tb_goods_visit'
        verbose_name = '统计分类商品访问量'
        verbose_name_plural = verbose_name