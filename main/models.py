from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserDetails(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_path = models.CharField(max_length=200, null=True)

class Stock(models.Model):
    ticker = models.CharField(max_length=10, null=False)
    security = models.CharField(max_length=100, null=False, default="")
    yahoo_urls = models.CharField(max_length=200, null=False)


class GSPCDATA(models.Model):
    date = models.DateField(null=False)
    open = models.FloatField(null=False)
    high = models.FloatField(null=False)
    low = models.FloatField(null=False)
    close = models.FloatField(null=False)
    volume = models.BigIntegerField(null=False)
    adj_close = models.FloatField(null=False)

