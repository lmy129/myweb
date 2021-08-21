from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

app_name = 'verifications'
urlpatterns = [
    path('image_codes/<uuid>/',views.ImagecodeView.as_view(),name='imagecode'),
]