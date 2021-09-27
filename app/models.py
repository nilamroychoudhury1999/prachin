from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User

import datetime
# Create your models here.

class Product(models.Model):
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    thumb = models.ImageField(default=None, blank=True)
    desc = models.CharField(max_length=300)
    
    def __str__(self):
        return self.product_name

class Order(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer = models.ForeignKey(User,on_delete=models.CASCADE)
    order_id = models.SlugField(max_length=100, null = False)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    address = models.CharField(max_length=50, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.get_username()