from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import timedelta

from django.utils import timezone


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsAnonymous(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CanEdit(BasePermission):
    def has_object_permission(self, request, view, obj):
        time_passed = timezone.now() - obj.created_at
        return time_passed < timedelta(minutes=10)


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            return False

        if request.method == "POST":
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return True