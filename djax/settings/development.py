from .base import *

CELERY_ALWAYS_EAGER = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DJAX_MAIN_TITLE = config('HUB_TITLE', default='Djax Action Hub')
DJAX_HUB_INSTANCE = config('HUB_INSTANCE', default='localhost')
DJAX_HUB_PROTOCOL = config('HUB_PROTOCOL', default='http')
DJAX_HUB_PORT = config('HUB_PORT', default='8000')
DJAX_LOOKER_INSTANCE = config('LOOKER_INSTANCE', default='localhost')
DJAX_INSTANCE_PROTOCOL = config('HUB_PROTOCOL', default='http')
DJAX_INSTANCE_API_PORT = config('HUB_API_PORT', default='19999')

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
