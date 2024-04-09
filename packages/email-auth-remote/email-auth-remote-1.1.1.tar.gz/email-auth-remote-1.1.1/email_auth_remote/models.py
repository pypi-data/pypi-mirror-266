from typing import Optional

from django.utils.functional import cached_property
from rest_framework_simplejwt.models import TokenUser


class CustomTokenUser(TokenUser):

    def save(self) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def delete(self) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def set_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def check_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def has_perm(self, perm: str, obj: Optional[object] = None) -> bool:
        """
        Return True if the user has the specified permission. Only works for superusers.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return False

    def has_module_perms(self, module: str) -> bool:
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return False

    @cached_property
    def short_name(self) -> str:
        return self.token.get("first_name", "")

    def get_short_name(self) -> str:
        return self.short_name
