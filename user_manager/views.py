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

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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

        # Check if the password matches
        if user.password != password:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Create refresh and access tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })