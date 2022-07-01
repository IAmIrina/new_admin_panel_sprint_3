import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')


class Command(BaseCommand):
    """Creating an admin user non-interactively if it doesn't exist.

    Uses enviroment varibles: SUPERUSER_USERNAME, SUPERUSER_PASSWORD, SUPERUSER_EMAIL

    """

    help = "Creates an admin user non-interactively if it doesn't exist"

    def handle(self, *args, **options):

        if not SUPERUSER_USERNAME:
            return

        User = get_user_model()
        if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
            User.objects.create_superuser(
                username=SUPERUSER_USERNAME,
                email=SUPERUSER_EMAIL,
                password=SUPERUSER_PASSWORD,
            )
