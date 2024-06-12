from django.contrib import admin
from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('change-password/', views.change_password, name='change_password'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.profile, name='profile'),
    path('password-reset-done/', views.password_reset_done, name='password_reset_done'),
    path('', views.home, name='home'),
]
