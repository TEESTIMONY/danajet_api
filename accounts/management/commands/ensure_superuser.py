import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a Django superuser from environment variables."

    def handle(self, *args, **options):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        username = os.getenv("DJANGO_SUPERUSER_USERNAME") or email

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser setup because DJANGO_SUPERUSER_EMAIL or "
                    "DJANGO_SUPERUSER_PASSWORD is not set."
                )
            )
            return

        User = get_user_model()
        lookup = {"email": email} if self._has_field(User, "email") else {"username": username}
        defaults = {
            "is_staff": True,
            "is_superuser": True,
        }

        if self._has_field(User, "email"):
            defaults["email"] = email
        if self._has_field(User, "username"):
            defaults["username"] = username

        user, created = User.objects.get_or_create(**lookup, defaults=defaults)

        for field, value in defaults.items():
            if getattr(user, field, None) != value:
                setattr(user, field, value)

        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin superuser: {email}"))

    def _has_field(self, model, field_name):
        return any(field.name == field_name for field in model._meta.fields)
