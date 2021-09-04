from functools import total_ordering
from django.shortcuts import render
#导入一个有序字典类
from collections import OrderedDict
from apps.goods.models import SKU, GoodsChannel,GoodsCategory
from apps.contents.models import ContentCategory
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views import View
from utils.goods import get_categories,get_breadcrumb
#导入Fdfs_client类用于创建实例上传文件，另外导入get_tracker_conf方法用于处理配置文件路径
#from fdfs_client.client import Fdfs_client,get_tracker_conf

# Create your views here.
#tracker_path = get_tracker_conf('utils/fastdfs/client.conf')

#client = Fdfs_client(tracker_path)

#上传成功会返回一个字典数据，字典中有可以访问这个文件的file_id
#client.upload_by_filename('/home/liumengyan/pkq.jpg')

class IndexView(View):
    
    def get(self,request):
        '''提供首页商品分类和首页广告数据'''

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
        return render(request,'index.html',context)

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


