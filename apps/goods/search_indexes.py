import datetime
#新建的类必须继承自这个类
from haystack import indexes 
#从要检索的子应用中导入要检索数据的数据模型
from .models import SKU

class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    '''建立一个索引类必须有且仅有一个字段document=True【在检索是这个字段是主要字段】
    并且建议所有子应用下建立的索引类都用同一个名称的字段document=True【一般都是text】可以改
    #se_template=True允许我们单独在一个文件中设置这个模型中的哪些字段参与检索
    这个文件一般在这【templates/search/indexes/子应用名/模型名小写_text.txt】'''
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        #设置要检索的模型类
        return SKU

    def index_queryset(self, using=None):
        """设置具体要检索的数据，查询结果集"""
        return self.get_model().objects.filter(is_launched=True)