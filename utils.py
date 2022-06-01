'''
@author: rkayondo
'''
import io
import logging
import random
import time
from functools import wraps

import numpy as np
import pandas as pd
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from redis import StrictRedis, ConnectionError

logger = logging.getLogger(__name__)


def isnum(self, input):
    try:
        float(input)
        return True
    except:
        return False


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        logging.info('func:%r took: %2.4f sec' % (f.__name__, te - ts))
        return result

    return wrap


def number_formatter(x):
    return '{:,}'.format(x)


def read_frame(values, **kw):
    """
    Transform a queryset to a pandas DataFrame
    """
    return pd.DataFrame.from_records(list(values), **kw)


def _eq(a, b, eps=0.0001):
    return abs(a - b) <= eps


def lock(key):
    """
    Because our server might fork, we need to use a Distributed Lock Manager (as opposed to global varibales)
    to handle locking. This decorator guarentees only one thread will be inside a function at a given time
    :param key: Name of lock
    :return:
    """

    def lock_decorator(f):
        @wraps(f)
        def wrap(*args, **kw):
            try:
                r = StrictRedis(connection_pool=settings.REDIS_CONN_POOL)
                lock_object = r.lock(key)
                acquired = lock_object.acquire()
                if not acquired:
                    raise ValueError("Could not acquire lock!")
                try:
                    result = f(*args, **kw)
                    return result
                finally:
                    if acquired:
                        lock_object.release()
            except ConnectionError as e:
                error_msg = "Could not connect to Redis"
                raise RuntimeError(error_msg, e)

        return wrap

    return lock_decorator


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def custom_round(x, base=10):
    if np.isnan(x):
        return "N/A"
    return int(base * round(float(x) / base))


def get_as_int(get, kword, converter=int):
    p = get.get(kword, None)
    if p:
        p = converter(p)
    return p


def get_as_float(get, kword):
    return get_as_int(get, kword, converter=float)
