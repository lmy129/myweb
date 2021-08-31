from django.urls import path
from . import views

app_name = 'areas'
urlpatterns = [
    path('areas/',views.AreasView.as_view(),name='province'),
    path('areas/<id>/',views.SubAreaView.as_view(),name='subareas'),
]