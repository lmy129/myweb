from django.urls import path
from . import views

app_name = 'verifications'
urlpatterns = [
    path('image_codes/<uuid:uuid>/',views.ImagecodeView.as_view(),name='imagecode'),
    path('sms_codes/<mobile:mobile>/',views.SmscodeView.as_view(),name='smscode'),
]