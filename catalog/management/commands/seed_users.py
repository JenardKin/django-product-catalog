import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

ADMINISTRATOR_GROUP = "Administrator"
READ_ONLY_GROUP = "Read only"
SEED_USERS = [
    {
        "username": "superuser",
        "first_name": "Test",
        "last_name": "Superuser",
        "email": "test.superuser@example.com",
        "password_env": "SEED_SUPERUSER_PASSWORD",
        "default_password": "Sup3rUs3r",
        "group": None,
        "is_superuser": True,
    },
    {
        "username": "administrator",
        "first_name": "Test",
        "last_name": "Administrator",
        "email": "test.administrator@example.com",
        "password_env": "SEED_ADMINISTRATOR_PASSWORD",
        "default_password": "Administr@tor",
        "group": ADMINISTRATOR_GROUP,
        "is_superuser": False,
    },
    {
        "username": "readonly",
        "first_name": "Test",
        "last_name": "Read Only",
        "email": "test.readonly@example.com",
        "password_env": "SEED_READONLY_PASSWORD",
        "default_password": "R3@d0nly",
        "group": READ_ONLY_GROUP,
        "is_superuser": False,
    },
]


class Command(BaseCommand):
    help = "Create the demo superuser, Administrator and Read only users and groups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Reset the password of users that already exist.",
        )

    def handle(self, *args, **options):
        catalog_permissions = Permission.objects.filter(
            content_type__app_label="catalog"
        )

        # Give catalog permissions and group read only
        administrators = self.handle_group(
            ADMINISTRATOR_GROUP,
            catalog_permissions
            | self.handle_auth_permissions("add_user", "change_user", "delete_user")
            | self.handle_auth_permissions("view_user", "view_group"),
        )
        # Read only: view permissions only (catalog models and users).
        read_only = self.handle_group(
            READ_ONLY_GROUP,
            catalog_permissions.filter(codename__startswith="view_")
            | self.handle_auth_permissions("view_user"),
        )
        groups = {ADMINISTRATOR_GROUP: administrators, READ_ONLY_GROUP: read_only}

        for spec in SEED_USERS:
            self.handle_user(
                spec, groups.get(spec["group"]), options["reset_passwords"]
            )

    @staticmethod
    def handle_auth_permissions(*codenames):
        return Permission.objects.filter(
            content_type__app_label="auth", codename__in=codenames
        )

    def handle_group(self, name, permissions):
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.set(permissions)
        self.stdout.write(f"Group '{name}': {permissions.count()} permissions")
        return group

    def handle_user(self, spec, group, reset_password):
        User = get_user_model()
        user, created = User.objects.update_or_create(
            username=spec["username"],
            defaults={
                "first_name": spec["first_name"],
                "last_name": spec["last_name"],
                "email": spec["email"],
                "is_staff": True,
                "is_superuser": spec["is_superuser"],
            },
        )
        if created or reset_password:
            password = os.environ.get(spec["password_env"], spec["default_password"])
            user.set_password(password)
            user.save()
        if group is not None:
            user.groups.set([group])
        state = "created" if created else "updated"
        self.stdout.write(f"User '{spec['username']}' {state}")
