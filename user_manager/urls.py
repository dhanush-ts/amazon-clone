from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('register/merchant/',views.MerchantView.as_view(), name='register-merchant'),
    path('register/user/',views.UserView.as_view(), name='register-user'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('products/', views.ProductAPIView.as_view(), name='products'),
    path('product/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product_detail'),
]