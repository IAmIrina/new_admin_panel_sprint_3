"""Django settings for config project."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    'components/database.py',
    'components/middleware.py',
    'components/templates.py',
    'components/installed_apps.py',
    'components/auth_password_validators.py',
)

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = json.loads(os.environ.get('ALLOWED_HOSTS', '["127.0.0.1"]'))

LOCALE_PATHS = ['movies/locale']

ROOT_URLCONF = 'config.urls'


WSGI_APPLICATION = 'config.wsgi.application'


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    "127.0.0.1",
]
