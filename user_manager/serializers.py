from rest_framework import serializers 
from .models import CustomUser, Merchant, User, Product

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'is_merchant', 'is_user', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class MerchantSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()  # Nested CustomUser serializer

    class Meta:
        model = Merchant
        fields = ['id', 'user', 'phone', 'business_name', 'business_address']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.create(**user_data)  # Create user object first
        merchant = Merchant.objects.create(user=user, **validated_data)  # Create merchant object with user
        return merchant

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            # Update user if data is passed
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        return super().update(instance, validated_data)

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
    user = CustomUserSerializer()

    class Meta:
        model = User
        fields = ['id', 'user', 'address']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.create(is_user=True, **user_data)  # Create user object with is_user set
        user_profile = User.objects.create(user=user, **validated_data)  # Create user profile
        return user_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            # Update user if data is passed
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        return super().update(instance, validated_data)