from functools import total_ordering
from django.http.response import HttpResponse
from django.shortcuts import render
#导入一个有序字典类
from collections import OrderedDict
from apps.goods.models import SKU, GoodsChannel,GoodsCategory
from apps.contents.models import ContentCategory
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views import View
from utils.goods import get_categories,get_breadcrumb,get_goods_specs
#导入Fdfs_client类用于创建实例上传文件，另外导入get_tracker_conf方法用于处理配置文件路径
#from fdfs_client.client import Fdfs_client,get_tracker_conf

# Create your views here.
#tracker_path = get_tracker_conf('utils/fastdfs/client.conf')

#client = Fdfs_client(tracker_path)

#上传成功会返回一个字典数据，字典中有可以访问这个文件的file_id
#client.upload_by_filename('/home/liumengyan/pkq.jpg')
class IndexView(View):
    
    def get(self,request):
        #提供首页商品分类和首页广告数据
        '''
        注释掉设置为静态化页面
        #提供商品分类数据
        categories = get_categories()

        contents = {}

        #从数据库中获取广告分类数据
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
        
        context = {
            'categories':categories,
            'contents':contents,
        }
        '''
        return render(request,'index.html')

class ListView(View):
    '''特定商品类别的商品列表数据'''
    def get(self,request,category_id):
        #这里传递了一个商品分类ID参数【当用户点击商品分类时获取对应分类的商品数据】
        
        #获取前端传递的分页信息【每页显示多少条数据】
        page_size = request.GET.get('page_size')

        #获取前端传递的显示第几页信息
        page = request.GET.get('page')

        #获取前端传递的排序信息【因为是get请求所以以查询字符串形式传递过来这里】
        ordering = request.GET.get('ordering')

        #获取category_id对应的商品分类，由于get方法查询不到时会引发错误所以使用try
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        
        #获取面包屑数据【面包屑就是点击对应的商品类别后显示在左上角的分类显示】
        breadcrumb = get_breadcrumb(category)

        #查询category商品分类下的商品数据【sku】
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)

        #给查询到的商品数据进行分页【使用Paginator类】
        #Paginator类的两个参数【1.要分页的数据列表，2.每页显示多少条数据】
        paginator = Paginator(skus,per_page=page_size)

        #将分页后的数据取出来
        page_skus = paginator.page(page)

        #初始化一个列表
        sku_list = []

        #将取出的分页后的数据转换成字典数据，以用于返回响应
        for sku in page_skus.object_list:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image_url,
            })

        #获取总页码
        total_num = paginator.num_pages

        #返回响应
        return JsonResponse({'code':0,'errmsg':'ok','breadcrumb':breadcrumb,'count':total_num,'list':sku_list})

class HotListView(View):
    '''热销商品列表'''
    def get(self,request,category_id):
        #获取分类商品数据
        try:
            category = GoodsCategory.objects.get(pk=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':0,'errmsg':'参数缺失'})
        
        #根据商品分类获取商品数据
        skus = SKU.objects.filter(category=category,is_launched=True).order_by('sales')

        hot_list = []
        for sku in skus[:5]:
            hot_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image_url,
                'sales':sku.sales,
            })
        return JsonResponse({'code':0,'errmsg':'ok','hot_list':hot_list})

from haystack.views import SearchView
class SKUSearchView(SearchView):
    '''定义查询数据的视图'''
    def create_response(self):
        #获取要查询的数据，haystack已经定义好了
        context = self.get_context()

        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append({
                'id':sku.object.id,
                'name':sku.object.name,
                'price':sku.object.price,
                'default_image_url':sku.object.default_image_url,
                'searchkey':context.get('query'),
                'page_size':context['page'].paginator.num_pages,
                'count':context['page'].paginator.count

            })
        
        #json默认是字典数据，这里是一个列表字典所以直接传递，然后加safe=False参数
        return JsonResponse(sku_list,safe=False)

'''
注释掉改为使用静态化页面
class DetailView(View):
    #定义商品详情页视图
    def get(self,request,sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass

        #获取分类数据
        categories = get_categories()

        #获取面包屑数据
        breadcrumb = get_breadcrumb(sku.category)

        #查询SKU规格信息
        goods_specs = get_goods_specs(sku)

        #整理返回数据
        context = {
            'categories':categories,
            'breadcrumb':breadcrumb,
            'sku':sku,
            'specs':goods_specs,
        }

        return render(request,'detail.html',context)
'''

def generic_meiduo_index():
    '''页面静态化函数,所谓页面静态化就是从数据库中查询数据渲染模板，然后将处理好的
    模板保存在目录中给用户访问，每次这个页面变化的时候就调用一次这个函数更新模板'''
    import time
    print('>>>>>>>>>>>>开始更新主页静态化页面%s>>>>>>>>>>>>>'% time.ctime())
    #提供商品分类数据
    categories = get_categories()

    contents = {}

    #从数据库中获取广告分类数据
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    
    context = {
        'categories':categories,
        'contents':contents,
    }
    #上面都是从数据库中查询数据，下面是渲染模板工作，分为三步
    #1.加载要渲染的模板
    from django.template import loader
    index_template = loader.get_template('index.html')
    #2.把数据给模板,渲染模板，获得渲染后的模板
    index_html_data = index_template.render(context)
    #3.把渲染好的模板，写入到指定文件【使用open()方法，参数：file要保存的路径，mode确定模式是读还是写，encoding指定编码方式】
    from meiduo_mall import settings
    import os
    #指定写入文件的路径和名称
    file_path = os.path.join(settings.BASE_DIR,'front_end_pc/index.html')
    #这里采用写模式，编码方式是utf-8,如果是读模式则'w'换成'r'
    with open(file_path,'w',encoding='utf-8') as f:
        #渲染后的模板数据写入指定文件目录
        f.write(index_html_data)

def generic_detail_html(sku):

    #获取分类数据
    categories = get_categories()

    #获取面包屑数据
    breadcrumb = get_breadcrumb(sku.category)

    #查询SKU规格信息
    goods_specs = get_goods_specs(sku)

    #整理返回数据
    context = {
        'categories':categories,
        'breadcrumb':breadcrumb,
        'sku':sku,
        'specs':goods_specs,
    }

    #加载模板
    from django.template import loader
    detail_template = loader.get_template('detail.html')

    #渲染模板
    detail_html_data = detail_template.render(context)

    #写入到指定文件
    import os
    from meiduo_mall import settings
    file_path = os.path.join(settings.BASE_DIR,'front_end_pc/goods/%s.html' % sku.id)

    with open(file_path,'w',encoding='utf-8') as f:
        f.write(detail_html_data)

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generic_detail_html(sku)


    