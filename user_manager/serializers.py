from rest_framework import serializers 
from .models import CustomUser, Merchant, User, Product

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'is_merchant', 'is_user', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class MerchantSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    business_name = serializers.CharField(write_only=True)
    business_address = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'username', 'phone', 'business_name', 'business_address']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class ProductSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer(read_only=True)  # Nested Merchant serializer

    class Meta:
        model = Product
        fields = ['id', 'merchant', 'name', 'price', 'quantity', 'description', 'created_at', 'updated_at', 'avg_rating', 'rating_count', 'category','image']
        read_only_fields = ['id', 'created_at', 'updated_at', 'avg_rating', 'rating_count']

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     merchant = Merchant.objects.get(user=request.user)
    #     validated_data['merchant'] = merchant  
    #     return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    address = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'username', 'address']
        extra_kwargs = {
            'password': {'write_only': True},
        }