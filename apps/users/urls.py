from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view(),name='usernamecount'),
    path('mobiles/<mobile:mobile>/count/',views.MobileCountView.as_view(),name='mobilecount'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
]