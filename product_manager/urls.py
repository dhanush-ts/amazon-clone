from django.urls import path
from .views import CartListView, CartCreateView, OrderView, OrderListView, ReviewView, ReviewDetails

urlpatterns = [
    path('cart/', CartListView.as_view()),
    path('cart/add/<int:id>/', CartCreateView.as_view()),
    path('order/', OrderView.as_view()),
    path('order/list/', OrderListView.as_view()),
    path('review-create/<int:id>/', ReviewView.as_view()),
    path('review/<int:id>/', ReviewDetails.as_view()),
]