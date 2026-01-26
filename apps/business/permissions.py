from rest_framework.permissions import BasePermission


class IsSuperAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False
