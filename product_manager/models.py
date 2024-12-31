from django.db import models
from user_manager.models import User, Product
import json
from django.core.validators import MinValueValidator, MaxValueValidator

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.user.username} - {self.product.name} (x{self.quantity})"
    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_items = models.TextField(default="[]")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} for {self.customer.user.username}"
    
    @property
    def cart_items_data(self):
        try:
            return json.loads(self.cart_items) 
        except json.JSONDecodeError:
            return []
        
class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review {self.id} for {self.product.name}"
    
class Return(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_returned = models.IntegerField(default=1, validators=[MinValueValidator(1),])
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Return {self.id} for {self.product.name}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'order', 'product'], 
                name='unique_return_per_product'
            )
        ]