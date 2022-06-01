import shlex
import subprocess

import os
from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    cmd = 'pkill -f /Users/newmanne/anaconda/envs/kudu2/bin/celery'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery -A agrotrade worker -l info --concurrency=1'
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting celery worker with autoreload...')
        autoreload.main(restart_celery)
