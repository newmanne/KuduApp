from agrotrade.settings.base import *

# TODO: If you start collaborating more, read values from a .env file that does not get checked in

DEBUG = True
SEND_SMS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'agrotrade',
        'USER': '',
        'PASSWORD': '',
    }
}

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware', ] + MIDDLEWARE
INSTALLED_APPS += ['debug_toolbar', 'django_extensions', ]
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ['rest_framework.permissions.AllowAny']
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = ['agrotrade.firebase_auth.authentication.FirebaseAuthentication']