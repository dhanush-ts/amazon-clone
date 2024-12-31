from django.urls import path
from .views import CartListView, CartCreateView, OrderView, OrderListView, ReviewView, ReviewDetails, ReturnView, ReturnDetails

urlpatterns = [
    path('cart/', CartListView.as_view()),
    path('cart/add/<int:id>/', CartCreateView.as_view()),
    path('order/', OrderView.as_view()),
    path('order/list/', OrderListView.as_view()),
    path('review-create/<int:id>/', ReviewView.as_view()),
    path('review/<int:id>/', ReviewDetails.as_view()),
    path('return/<int:order_id>/<int:product_id>/', ReturnView.as_view()),
    path('order/<int:order_id>/return/', ReturnDetails.as_view()),
]