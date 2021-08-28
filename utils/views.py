'''
重写django内置视图的一些不满足要求的方法
'''
#这是一个django内置的验证用户是否登录的类，因为返回的不是json数据所以这里
#重写其中的handle_no_permission()方法，让其返回json数据
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.http import JsonResponse

class NewLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code':400,'errmsg':'用户未登录'})