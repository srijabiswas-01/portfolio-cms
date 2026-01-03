import os
import sys

from django.core.exceptions import ImproperlyConfigured


def configure_django_settings() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio_project.settings")


def main() -> None:
    configure_django_settings()
    import django

    django.setup()
    from django.contrib.auth import get_user_model

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

    if not username or not password:
        return

    User = get_user_model()
    user, _ = User.objects.get_or_create(username=username, defaults={"email": email})
    user.email = email or user.email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()


if __name__ == "__main__":
    try:
        main()
    except ImproperlyConfigured as exc:
        sys.stderr.write(f"Skipped creating superuser: {exc}\n")
