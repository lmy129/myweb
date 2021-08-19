from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    #这里要注意在匹配路由的时候开头不能带有'/'，但是最后结尾一定要带'/'
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view(),name='usernamecount'),
    path('mobiles/<mobile:mobile>/count/',views.UsermobileCountView.as_view(),name='usermobilecount'),
]