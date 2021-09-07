#导入需要用到的模块【注意，是写在要运行的django  py文件中】
import sys
import os
import django

 
#../意思是当前目录的上一级目录，一般定义到BASE_DIR
sys.path.insert(0,'./')
 
#指定当前django项目中的配置文件在哪里
os.environ.setdefault('DJANGO_SETTINGS_MODULE',"meiduo_mall.settings")
 
#setup方法将django运行的需要以来的东西导入进来
django.setup()


from utils.goods import get_breadcrumb,get_categories
from apps.goods.models import SKU

def generic_detail_html(sku):

    #获取分类数据
    categories = get_categories()

    #获取面包屑数据
    breadcrumb = get_breadcrumb(sku.category)


    #整理返回数据
    context = {
        'categories':categories,
        'breadcrumb':breadcrumb,
        'sku':sku,
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
        print('%s商品详情页创建成功' % sku.id)
