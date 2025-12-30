from django.apps import AppConfig


class PublicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public'

    def ready(self):
        # Import checks so Django registers them when the app is ready.
        import apps.public.checks  # noqa: F401

