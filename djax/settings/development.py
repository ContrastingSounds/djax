from .base import *

CELERY_ALWAYS_EAGER = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='jonathan.walls+dev_djax@looker.com')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ALLOWED_HOSTS = [
    'jwtest.ngrok.io',
    'jwtestapi.ngrok.io',
    'localhost',
    '127.0.0.1',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config('HUB_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('HUB_EMAIL_HOST_PASSWORD')
