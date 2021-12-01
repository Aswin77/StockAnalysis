from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('stock/<str:ticker>', views.stock, name='stock'),
]