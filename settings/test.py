from agrotrade.settings.base import *
DEBUG = True
SEND_SMS = False

ALLOWED_HOSTS = ['localhost','127.0.0.1', 'kudutest', '137.82.155.99','www.kudu-test.cs.ubc.ca', 'kudu-test.cs.ubc.ca']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware',] + MIDDLEWARE
INSTALLED_APPS += ['debug_toolbar',]