from rest_framework.permissions import BasePermission


class IsGerenteOrAdmin(BasePermission):

    def has_permission(self, request, view):
        usuario = request.user

        return (
            usuario.is_authenticated
            and (
                usuario.is_superuser
                or usuario.groups.filter(name="Gerente").exists()
            )
        )