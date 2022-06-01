
from agrotrade_celery import app as celery_app
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrotrade.settings.production')
os.environ.setdefault('MPLCONFIGDIR', '/tmp/')

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
__all__ = ['celery_app']