import json
import logging

import requests
from celery.result import AsyncResult
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from agrotrade.firebase_auth.authentication import get_uid
from agrotrade.models import *
from agrotrade.sms_market import process_msg
from agrotrade.tasks import check_new_saved_search_matches
from agrotrade.seller import make_ask

logger = logging.getLogger(__name__)


def main_handler(request):
    try:
        sender = request.GET['sender']
        message = request.GET['message']
    except KeyError as e:
        logger.error(f"An exception occured processing message {request}")
    process_msg(sender, message)
    return HttpResponse(status=200)


def file_not_found_404(request):
    page_title = 'Resource not found: 404'
    return render(request, '404.html', locals())


def server_error_500(request):
    page_title = 'Server Error: 500'
    return render(request, '500.html', locals())


#### CELERY CALLS ####
def check_task(task_id, task=None):
    if task is None:
        task = AsyncResult(task_id)
    status = task.status
    ready = task.ready()
    retval = {
        'ready': ready,
        'task_id': task_id,
        'status': status
    }
    if ready:
        result = task.get(propagate=False)
        if isinstance(result, Exception):
            traceback = task.traceback
            retval['error'] = str(result)
            retval['traceback'] = traceback
            return HttpResponse(json.dumps(retval), content_type='application/json')
        else:
            retval['result'] = result
            return HttpResponse(json.dumps(retval), content_type='application/json')
    else:
        return HttpResponse(json.dumps(retval), content_type='application/json')


def check_task_url(request, task_id):
    return check_task(task_id)

def send_notifications(request):
    check_new_saved_search_matches()
    return HttpResponse("")
