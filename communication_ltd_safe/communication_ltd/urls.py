from django.contrib import admin
from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('change-password/', views.change_password, name='change_password'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('enter-passcode/', views.enter_passcode, name='enter_passcode'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
]
