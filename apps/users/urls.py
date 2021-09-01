from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view(),name='usernamecount'),
    path('mobiles/<mobile:mobile>/count/',views.MobileCountView.as_view(),name='mobilecount'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('info/',views.CenterView.as_view(),name='info'),
    path('emails/',views.EmailView.as_view(),name='email'),
    path('activation_emails/',views.ActivationEmailView.as_view(),name='activationemails'),
    path('addresses/create/',views.CreateAddressView.as_view(),name='createaddress'),
    path('addresses/',views.AddressView.as_view(),name='addresses'),
]