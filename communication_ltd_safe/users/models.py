from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)

class Customer(AbstractBaseUser):
    email = models.EmailField(unique=True)
    surfing_packages = models.JSONField(default=list)
    new_customer_name = models.JSONField(default=list) 
    reset_token = models.CharField(max_length=40, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    # Fields for tracking login attempts
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class UserPasswordHistory(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'password')
