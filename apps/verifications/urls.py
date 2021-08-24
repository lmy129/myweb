from django.urls import path
from . import views

app_name = 'verifications'
urlpatterns = [
    path('image_codes/<uuid:uuid>/',views.ImageCodeView.as_view(),name='image_code'),
    path('sms_codes/<mobile:mobile>/',views.SmsCodeView.as_view(),name='smscode'),
]