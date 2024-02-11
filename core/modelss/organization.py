from django.db import models

class Organization(models.Model):
    '''Organization which a user can belong to'''
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    about = models.TextField()
    location = models.CharField(max_length=255)
    