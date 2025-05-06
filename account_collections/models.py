from django.db import models
from django.contrib.auth.models import User

#Handles storage of collection and items in database

class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link collection to user
    name = models.CharField(max_length=255)
    theme = models.CharField(max_length=255)
    description = models.TextField()
    

    def __str__(self):
        return self.name

class Item(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    theme = models.CharField(max_length=255)
    description = models.TextField()
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_purchased = models.DateField()
    #adding images to model to display under collections
    #url to access image
    image = models.ImageField(upload_to='items/images/', null=True, blank=True)

    def __str__(self):
        return self.name
