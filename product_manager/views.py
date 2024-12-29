from django.shortcuts import render
from rest_framework import generics
from .models import Cart, Order, Review
from user_manager.models import Product, User
from .serializer import CartSerializer, OrderSerializer, OrderListSerializer, ReviewSerializer
from user_manager.permissions import IsUser
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import json
from user_manager.permissions import IsUserOrReadOnly

class CartCreateView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsUser]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError("Authentication is required.")
        user = User.objects.get(user=user)
        product_id = self.kwargs.get('id')
        if not product_id:
            raise ValidationError("Product ID is required in the URL.")
        product = get_object_or_404(Product, id=product_id)
        existing_cart_item = Cart.objects.filter(customer=user, product=product).first()
        if existing_cart_item:
            new_quantity = existing_cart_item.quantity + serializer.validated_data.get('quantity', 1)
            existing_cart_item.delete()
            serializer.save(customer=user, product=product, quantity=new_quantity)
        else:
            serializer.save(customer=user, product=product)
    
class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsUser]
    
    def get_queryset(self):
        user = self.request.user
        user = User.objects.get(user=user)
        return Cart.objects.filter(customer=user)
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsUser]
    
    def get_queryset(self):
        user = self.request.user
        user = User.objects.get(user=user)
        return Order.objects.filter(customer=user)

class OrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsUser]
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError("Authentication is required.")
        user = User.objects.get(user=user)
        cart_items = Cart.objects.filter(customer=user)
        total = 0
        cart_items_data = []
        if len(cart_items) == 0:
            raise ValidationError("Cart is empty.")
        for i in cart_items:
            total += i.product.price * i.quantity
            product = i.product
            if i.quantity > product.quantity:
                raise ValidationError(f"Not enough quantity for product {product.name}. Only {product.quantity} available.")
            product.quantity -= i.quantity
            product.save()
            item_data = {
                'product_id': product.id,
                'product_name': product.name,
                'quantity': i.quantity,
                'price': float(i.product.price),
                'total_price': float(i.product.price * i.quantity)
            }
            cart_items_data.append(item_data)
            i.delete()
        cart_items_json = json.dumps(cart_items_data)
        serializer.save(customer=user, total_amount=total, cart_items=cart_items_json)
        self.response = {"total_amount": total, "cart_items": cart_items_data}

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(self.response)

class ReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        product_id = self.kwargs.get('id')
        if not product_id:
            raise ValidationError("Product ID is required in the URL.")
        product = get_object_or_404(Product, id=product_id)
        return Review.objects.filter(product=product)

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.kwargs.get('id')
        if not product_id:
            raise ValidationError("Product ID is required in the URL.")
        product = get_object_or_404(Product, id=product_id)
        user = User.objects.get(user=user)
        user_orders = Order.objects.filter(customer=user)
        ordered_products = []
        for order in user_orders:
            ordered_products.extend(order.cart_items_data)
        product_found = False
        for item in ordered_products:
            item_id = item.get('product_id', 0)
            if int(product_id) == int(item_id):
                product_found = True
                break
        if not product_found:
            raise ValidationError("You can only review a product you have ordered.")
        serializer.save(customer=user, product=product)

class ReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsUserOrReadOnly]
    lookup_field = 'id'
    queryset = Review.objects.all()