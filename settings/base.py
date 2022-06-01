# Django settings for Agrotrade project.

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

ADMINS = (
    ('Kudu Admins', ''),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
USE_THOUSAND_SEPARATOR = True
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

from django.utils.translation import ugettext_lazy as _

LANGUAGES = (
    ('en-us', _('English')),
    ('lug', _('Luganda')),
    ('luo', _('Luo')),
    ('run', _('Runyakitara')),
    ('es', _('Spanish')),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'agrotrade', 'locale'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'agrotrade',
        'USER': '',
        'PASSWORD': '',
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media
# /media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'agrotrade', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'TODO'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [''],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agrotrade.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'agrotrade',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_filters',
    'rest_framework_gis',
    'django_filters',
    'crispy_forms',
    'corsheaders',
    'agrotrade.firebase_auth',
    'push_notifications',
    'phonenumber_field',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'agrotrade.firebase_auth.authentication.FirebaseAuthentication'
    ],
    'DEFAULT_FILTER_BACKENDS': ['rest_framework_filters.backends.RestFrameworkFilterBackend',
                                'rest_framework.filters.OrderingFilter'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

CORS_ORIGIN_ALLOW_ALL = True  # TODO!!!

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler'
        # },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, 'logs', 'kudu.log'),
            'formatter': 'simple',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        # 'agrotrade.clearing': {
        #     'handlers': ['file', 'console'],
        #     'level': 'INFO',
        #     'propagate': True
        # }
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': True,
        # },
    }
}
ALLOWED_HOSTS = ['localhost']]

AUTH_PROFILE_MODULE = "agrotrade.UserProfile"

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/latest/'

LOG_FILE = os.path.join(PROJECT_DIR, 'logs', 'smskudu.log')
LOG_USSD = os.path.join(PROJECT_DIR, 'logs', 'ussdkudu.log')
LOG_AUDIT = os.path.join(PROJECT_DIR, 'logs', 'audit.log')

INTERNAL_IPS = ['127.0.0.1']
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = " u'Kampala'"
EMAIL_USE_TLS = True

# CACHE STUFF

# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#    }
# }
import redis

REDIS_CONN_POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': [
            'localhost:6379',
        ],
        'OPTIONS': {
            'DB': 1,
            # 'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            'MAX_CONNECTIONS': 1000,
            'PICKLE_VERSION': -1,
        },
    },
}

SEND_SMS = True
USE_TZ = True
TIME_ZONE = 'Africa/Nairobi'
KEYFILES_DIR = os.path.join(PROJECT_DIR, 'keyfiles')
FIREBASE_KEY = 'firebase_key.json'

# https://github.com/jazzband/django-push-notifications
PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": "",
}
