from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager




class UserManager(BaseUserManager):
    '''Manager for user'''
    def create_user(self, email, password, first_name, last_name, role, **extra_fields):
        '''create a general user'''
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=email, first_name=first_name, last_name=last_name, role=role, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user
    def create_superuser(self, email, password,  first_name, last_name, **extra_fields):
        '''create a super user'''
        user = self.create_user(email, password, first_name, last_name, 'SUPER_USER')
        
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    '''User in the system'''
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=50)

    USERNAME_FIELD = 'email'

    objects = UserManager()





    


