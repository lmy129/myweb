from django.urls import path
from . import views

app_name = 'verifications'
urlpatterns = [
    path('image_codes/<uuid:uuid>/',views.ImagecodeView.as_view(),name='imagecode'),
]