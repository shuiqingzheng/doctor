from rest_framework.permissions import BasePermission


class TokenHasPermission(BasePermission):

    def has_permission(self, request, view):
        token = request.auth

        if not token:
            return False

        return True
