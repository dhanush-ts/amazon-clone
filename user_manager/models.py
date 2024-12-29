from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    is_merchant = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # def check_password(self, raw_password):
    #     return super().check_password(raw_password)
    
    def save(self, *args, **kwargs):
        # Automatically set is_merchant or is_user based on Merchant relationship
        if hasattr(self, 'merchant_profile'):
            self.is_merchant = True
            self.is_user = False
        elif hasattr(self, 'user_profile'):
            self.is_user = True
            self.is_merchant = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# Merchant Model
class Merchant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='merchant_profile')
    phone = models.CharField(max_length=10, default="0000000000", validators=[RegexValidator(r'^\d{10}$', 'Phone number must be exactly 10 digits')])
    business_name = models.CharField(max_length=100)
    business_address = models.CharField(max_length=100)
    
    def save(self, *args, **kwargs):
        # Set is_merchant to True and is_user to False when creating a merchant profile
        self.user.is_merchant = True
        self.user.is_user = False
        self.user.save()  # Save the user to update the fields

        super().save(*args, **kwargs)  #

    def __str__(self):
        return f'{self.user.username} - {self.business_name}'


# Product Model
class Product(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avg_rating = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    category = models.CharField(max_length=50, default="General")
    image = models.ImageField(upload_to='products/')
    
    def __str__(self):
        return f'{self.name} - {self.merchant.business_name}'

    def update_avg_rating(self, new_rating):
        if self.rating_count > 0:
            self.avg_rating = ((self.avg_rating * self.rating_count) + new_rating) / (self.rating_count + 1)
            self.rating_count += 1
        else:
            self.avg_rating = new_rating
            self.rating_count = 1
        self.save()


# User Model (for normal users)
class User(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    address = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        # Set is_merchant to True and is_user to False when creating a merchant profile
        self.user.is_merchant = False
        self.user.is_user = True
        self.user.save()  # Save the user to update the fields

        super().save(*args, **kwargs)  #

    def __str__(self):
        return self.user.username