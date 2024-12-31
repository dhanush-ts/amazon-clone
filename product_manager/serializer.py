from rest_framework import serializers
from .models import Cart, Order, Review, Return

class CartSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    product = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Cart
        fields = '__all__'
        
    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     if not request or not request.user:
    #         raise serializers.ValidationError("Request context with authenticated user is required.")

    #     user = request.user 
    #     product = validated_data.get('product')
    #     quantity = validated_data.get('quantity', 1)

    #     existing_cart_item = Cart.objects.filter(customer=user, product=product).first()

    #     if existing_cart_item:
    #         new_quantity = existing_cart_item.quantity + quantity
    #         existing_cart_item.delete()
    #         validated_data['quantity'] = new_quantity

    #     validated_data['customer'] = user

    #     return super().create(validated_data)
    
class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    cart_items = CartSerializer(many=True,read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
    
class OrderListSerializer(serializers.ModelSerializer):
    cart_items_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        exclude = ["cart_items",]
        
    def get_cart_items_data(self, obj):
        return list(obj.cart_items_data)
    
class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    customer = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        
class ReturnSerializer(serializers.ModelSerializer):
    order = serializers.StringRelatedField(read_only=True)
    product = serializers.StringRelatedField(read_only=True)
    customer = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Return
        fields = '__all__'