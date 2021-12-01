from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.index, name='index'),
    path('about', views.aboutus, name='about'),
    path('contact', views.contactus, name='contact'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
]