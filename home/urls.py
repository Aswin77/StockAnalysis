from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('profile/', views.profile, name="profile"),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('stock_list/', views.stock_list, name="stock_list"),
    path('watchlist/', views.watchlist, name="watchlist"),
    path('history/', views.history, name="history"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

