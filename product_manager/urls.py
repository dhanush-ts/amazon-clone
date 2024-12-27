from django.urls import path
from .views import CartListView, CartCreateView, OrderView, OrderListView

urlpatterns = [
    path('cart/', CartListView.as_view()),
    path('cart/add/<int:id>/', CartCreateView.as_view()),
    path('order/', OrderView.as_view()),
    path('order/list/', OrderListView.as_view()),
]