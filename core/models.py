from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings




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
    

    def create_superuser(self, email, password,  first_name='N/A', last_name='N/A', **extra_fields):
        '''create a super user'''
        user = self.create_user(email, password, first_name, last_name, 'SUPER_USER')
        
        user.is_superuser = True
        user.is_staff = True
        
        user.save(using=self._db)

        return user
    


class Organization(models.Model):
    '''Organization which a user can belong to'''
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    about = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    logo_pic_url = models.CharField(max_length=500, default="")
    created_at = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    '''Locations for the organizations'''
    location = models.TextField()
    description = models.TextField()
    organization = models.ForeignKey(
        Organization,
        on_delete=models.DO_NOTHING
    )

class User(AbstractBaseUser, PermissionsMixin):
    '''User in the system'''
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=50)
    orgnaization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='members'
    )
    profile_pic_url = models.CharField(max_length=500, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Visitor(models.Model):
    '''Visitor in the system'''
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    profile_pic_url = models.CharField(max_length=500, default="")
    address = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

class InvitationPass(models.Model):
    '''Invitation for a visitor by user'''
    valid_from = models.DateTimeField()
    valid_till = models.DateTimeField()
    purpose = models.TextField()
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.DO_NOTHING
    )
    inv_created_at = models.DateTimeField(auto_now_add=True)
    organization_location = models.ForeignKey(
        Location,
        on_delete=models.DO_NOTHING
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='created_by'
    )
    visiting_person = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='visiting_person'
    )
    checked_in_at = models.DateTimeField()
    checked_out_at = models.DateTimeField()
    feedback = models.TextField()
    rating = models.FloatField()

class InvitationStatus(models.Model):
    '''Keep records of all the statuses an Invitation goes through'''
    invitation = models.ForeignKey(
        InvitationPass,
        on_delete=models.DO_NOTHING
    )
    current_status = models.CharField(max_length=30)
    next_status = models.CharField(max_length=30)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Belonging(models.Model):
    '''Items carried by a visitor while checked in'''
    name = models.CharField(max_length=50)
    description = models.TextField()
    invitation = models.ForeignKey(
        InvitationPass,
        on_delete=models.DO_NOTHING
    )
    identifier_code = models.CharField(max_length=100) #eg: laptop serial number


class Item(models.Model):
    '''Items collection for auto populate '''
    name = models.CharField(max_length=50)
    item_description = models.TextField()
    is_allowed = models.BooleanField(default=True)

















    







    

