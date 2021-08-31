from django.shortcuts import render
from apps.areas.models import Area
from django.http import JsonResponse
from django.views import View
# Create your views here.
class AreasView(View):
    #定义获取省份视图，当用户点击管理地址页面的时候前端获取省份数据，当选择省份后再次查询市数据
    def get(self,request):
        #首先从模型中查询省份数据，因为省份是最高级所以没有parent_id也就是在数据库里null所以按照None查询
        provinces = Area.objects.filter(parent=None)
        #provinces获取到的是查询结果集包含的数据是对象不是字典，不能直接返回给前端【因为前端需要Json数据】，这里进行转换
        provinces_list = []
        for province in provinces:
            provinces_list.append({
                'id':province.id,
                'name':province.name,
            })
        return JsonResponse({'code':0,'errmsg':'ok','province_list':provinces_list})

class SubAreaView(View):
    #定义选择省份后查询市、区视图，注意这里是市、区一起公用一个路由和视图
    def get(self,request,id):
        #先获取省份信息，这里使用get方法因为只有一个结果，若果使用filter再使用subs.all()将发生错误
        #因为filter不止一个结果的时候才使用，而get是明确只有一个结果的时候使用
        up_level = Area.objects.get(pk=id)
        #根据上一级获取下一级数据，由于点击选中省份和市的时候前端会自动发送请求，携带数据id所以这里使用一个
        #视图和路由就可以同时解决选择省份查询市和选择市查询区的功能
        down_level = up_level.subs.all()
        #将得到的查询结果集转换为字典以作为Json数据响应
        data_list = []
        for item in down_level:
            data_list.append({
                'id':item.id,
                'name':item.name,
            })
        return JsonResponse({'code':0,'errmsg':'ok','sub_data':{'subs':data_list}})




