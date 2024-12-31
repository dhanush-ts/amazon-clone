from django.shortcuts import render
from rest_framework import generics
from .models import Cart, Order, Review, Return
from user_manager.models import Product, User
from .serializer import CartSerializer, OrderSerializer, OrderListSerializer, ReviewSerializer, ReturnSerializer
from user_manager.permissions import IsUser
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import json
from datetime import timedelta
from django.utils import timezone
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
    
class ReturnView(generics.CreateAPIView):
    serializer_class = ReturnSerializer
    permission_classes = [IsUserOrReadOnly]

    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        product_id = self.kwargs.get('product_id')

        if not order_id or not product_id:
            raise ValidationError("Order ID and Product ID are required in the URL.")

        order = get_object_or_404(Order, id=order_id)
        product = get_object_or_404(Product, id=product_id)
        user = self.request.user
        user = get_object_or_404(User, user=user)

        if self.request.user != order.customer.user:
            raise ValidationError("You are not the order's customer.")
        
        retu = Return.objects.filter(product=product, order=order)
        if retu.exists():
            raise ValidationError("Product already returned.")
        time_difference = timezone.now() - order.created_at
        if time_difference > timedelta(hours=24):
            raise ValidationError("Product can only be returned within 24 hours of the order.")


        for i in order.cart_items_data:
            if int(i['product_id']) == int(product.id):
                if int(i['quantity']) >= int(self.request.data.get("quantity")):
                    product.quantity += int(self.request.data.get("quantity"))
                    product.save()
                    return_instance = serializer.save(product=product,order=order,customer=user, quantity_returned=int(self.request.data.get('quantity')))
                    return return_instance
                else:
                    raise ValidationError("Not enough quantity to return.")
        raise ValidationError("Product not found in the order.")

class ReturnDetails(generics.ListAPIView):
    serializer_class = ReturnSerializer
    permission_classes = [IsUserOrReadOnly]
    lookup_field = 'order_id'
    
    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        return Return.objects.filter(order__id=order_id)