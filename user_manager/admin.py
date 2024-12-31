from django.contrib import admin
from .models import CustomUser, Merchant, Product, User

# Custom User Admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_merchant', 'is_user', 'date_joined')
    search_fields = ('email', 'username')
    list_filter = ('is_merchant', 'is_user', 'is_staff', 'is_active')
    ordering = ('-date_joined',)

admin.site.register(CustomUser, CustomUserAdmin)

# Merchant Admin
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'phone', 'business_address')
    search_fields = ('user__username', 'business_name')
    list_filter = ('user__is_merchant',)

admin.site.register(Merchant, MerchantAdmin)

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant', 'price', 'quantity', 'category', 'created_at', 'avg_rating')
    search_fields = ('name', 'merchant__business_name', 'category')
    list_filter = ('category',)
    ordering = ('-created_at',)

admin.site.register(Product, ProductAdmin)

# User Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username', 'address')
    
admin.site.register(User, UserAdmin)
