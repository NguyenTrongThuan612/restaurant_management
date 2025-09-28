from rest_framework import permissions
from app_core.models.user import UserRole

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.MANAGER

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.EMPLOYEE