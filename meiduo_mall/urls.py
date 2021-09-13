"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

#导入路径转换器，这里放在项目主url里是为了，这样其他应用也可以直接在路由使用路径转换器
from utils.converters import UsernameConverter,MobileCoverter,UuidCoverter
from django.urls import register_converter

register_converter(UsernameConverter,'username')
register_converter(MobileCoverter,'mobile')
register_converter(UuidCoverter,'uuid')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('apps.users.urls',namespace='users')),
    path('',include('apps.verifications.urls',namespace='verifications')),
    path('',include('apps.areas.urls',namespace='areas')),
    path('',include('apps.goods.urls',namespace='goods')),
    path('',include('apps.carts.urls',namespace='carts')),
]
