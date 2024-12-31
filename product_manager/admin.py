from django.contrib import admin
from .models import Cart, Order, Review, Return

# Register your models here.
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Return)