from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

# Override Admin login template for "View Site Button" on login page.
admin.site.login_template = "catalog/admin_login.html"


admin.site.unregister(User)


@admin.register(User)
class RestrictedUserAdmin(UserAdmin):
    """
    Custom User Admin that ensures superusers cannot
    change or delete other superusers;
    and set is_superuser and user_permissions fields as read-only for
    non-superusers. Other staff with the "change user" permission can still
    """

    @staticmethod
    def is_other_superuser(request, obj):
        return obj is not None and obj.is_superuser and obj != request.user

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly = (*readonly, "is_superuser", "user_permissions")
        return readonly

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(
            request, obj
        ) and not self.is_other_superuser(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj == request.user:
            return True
        return super().has_delete_permission(
            request, obj
        ) and not self.is_other_superuser(request, obj)
