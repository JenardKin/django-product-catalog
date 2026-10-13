from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = (
        "django.db.models.BigAutoField"  # change primary key to 64-bit integer
    )
    name = "catalog"

    def ready(self):
        # import to register user login/logout signal handlers
        from . import signals  # noqa: F401
