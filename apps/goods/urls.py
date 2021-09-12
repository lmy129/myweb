from django.urls import path
from . import views

app_name = 'goods'
urlpatterns = [
    #path('index/',views.IndexView.as_view(),name='index'),
    path('list/<category_id>/skus/',views.ListView.as_view(),name='listsku'),
    path('hot/<category_id>/',views.HotListView.as_view(),name='hotlist'),
    path('search/',views.SKUSearchView(),name='skusearch'),
    path('detail/visit/<category_id>/',views.CategoryVisitCountView.as_view(),name='skuvisit'),
    #path('goods/<sku_id>.html/',views.DetailView.as_view(),name='detail'),
]