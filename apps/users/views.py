from django.shortcuts import render
from django.views import View
from .models import User
from django.http import JsonResponse
import re

# Create your views here.
class UsernameCountView(View):
    #定义检查用户名个数视图
    def get(self,request,username):
        #django接收URL路径中的参数使用尖括号，如果没有过滤器【例如<int:id>】则接收除'/'外的所有字符
        #if re.match('[a-zA-Z0-9_-]{5,20}',username): [因为使用了自定义的转换器所以视图中不再使用条件判断]
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})
        #else:
            #return JsonResponse({'code':200,'errmsg':'用户名不满足需求'})
