from django.shortcuts import render
#导入一个有序字典类
from collections import OrderedDict
from apps.goods.models import GoodsChannel
from django.views import View

def get_categories():
    '''提供首页商品分类数据'''
    #查询商品频道和分类

    #创建一个有序字典
    categories = OrderedDict()
    #获得需要数据的查询结果集，先按照组号进行排序，再按照序号进行排序
    channels = GoodsChannel.objects.order_by('group_id','sequence')
    for channel in channels:
        group_id = channel.group_id

        #判断如果当前对象的组号不在有序字典里则初始化，关于这个对象的数据存储结构
        if group_id not in categories:
            categories[group_id] = {'channels':[],'sub_cats':[]}

        #当前频道的类别
        cat1 = channel.category

        #追加当前频道
        categories[group_id]['channels'].append({
            'id':cat1.id,
            'name':cat1.name,
            'url':channel.url
        })

        #构建当前类别的子类别
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories


#面包屑
def get_breadcrumb(category):
    #接收最低级别的类别，获取各个类别的名称，返回
    
    dict = {
        'cat1':'',
        'cat2':'',
        'cat3':'',
        }
    if category.parent == None:
        #判断如果parent没有值，则证明是一级分类
        dict['cat1'] = category.name

    elif category.parent.parent == None:
        #判断如果category的parent的parent没有值，则证明是二级分类
        dict['cat2'] = category.name
        dict['cat1'] = category.parent.name

    else:
        #否则就是三级分类
        dict['cat3'] = category.name
        dict['cat2'] = category.parent.name

    return dict

'''def get_goods_specs(sku):
    #获取商品规格信息
    sku_specs = sku.skuspecification_set.filter(sku=sku).order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    #获取当前商品的所有SKU
    skus = sku.spu.sku_set.all()
    #构建不同规格参数选项的sku字典
    spec_sku_map = {}
    for s in skus:
        #获取sku的规格参数
        s_specs = s.specs.order_by('spec_id')
        #用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        #向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    #以下代码为：在每个选项上绑定对应的sku_id值
    #获取当前商品的规格信息
    goods_specs = sku.spu.specs.order_by('id')
    #若当前sku的规格信息不完整，则不在继续
    if len(sku_key) < len(goods_specs):
        return
    for index,spec in enumerate(goods_specs):
        #复制当前sku的规格键
        spec_options = spec.options.all()
        for option in spec_options:
            #在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.spec_options = spec_options
    return goods_specs'''