from django.db import models
from django.contrib.auth.models import User
from main.models import Stock
# Create your models here.

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10, default=0)
    security = models.CharField(max_length=100, default=0)

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True)
    datetime = models.DateTimeField(auto_now_add=True)