from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User, Merchant

class IsMerchant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_merchant

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Merchant):
            return obj.user == request.user and request.user.is_merchant
        return False

class IsMerchantorReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.merchant.user == request.user

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_merchant
    

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_user

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj.user == request.user
        return False