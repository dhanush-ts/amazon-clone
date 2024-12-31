from rest_framework import viewsets
from .models import CustomUser, Merchant, Product, User
from .serializers import CustomUserSerializer, MerchantSerializer, ProductSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import CustomUser
from rest_framework import generics
from user_manager.permissions import IsMerchantorReadOnly, IsMerchant

class ProductAPIView(generics.ListCreateAPIView):
    permission_classes = [IsMerchantorReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        merchant = Merchant.objects.get(user=user)
        serializer.save(merchant=merchant)
    
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMerchantorReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class UserView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        email = self.request.data.get('email')
        address = self.request.data.get('address')
        custom_user = CustomUser.objects.create_user(username=username, email=email, password=password)
        User.objects.create(user=custom_user, address=address)
        serializer.instance = custom_user
        
class MerchantView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = MerchantSerializer
    
    def perform_create(self, serializer):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        email = self.request.data.get('email')
        business_address = self.request.data.get('business_address')
        business_name = self.request.data.get('business_name')
        phone = self.request.data.get('phone')
        custom_user = CustomUser.objects.create_user(username=username, email=email, password=password)
        Merchant.objects.create(user=custom_user, business_address=business_address, phone=phone, business_name=business_name)
        serializer.instance = custom_user

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        if user.password != password:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })