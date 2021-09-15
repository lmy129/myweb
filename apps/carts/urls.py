from django.urls import path
from . import views

app_name = 'carts'
urlpatterns = [
    path('carts/',views.CartsView.as_view(),name='carts')
]