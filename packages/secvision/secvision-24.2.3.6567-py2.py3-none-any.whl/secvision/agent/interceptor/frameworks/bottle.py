# Copyright (c)
# All Rights Reserved

"""Interceptor for Bottle.

"""

import sys

from ssecvision.agent.interceptor.frameworks.wsgi import WSGIInterceptor
from ssecvision.agent.interceptor.base import BaseInterceptor


class BottleInterceptor(BaseInterceptor):
    def add_exception(self, func, *args, **kwargs):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*sys.exc_info())
        return func(*args, **kwargs)


def intercept_bottle(agent, mod):
    WSGIInterceptor(agent, mod.Bottle).attach('__call__')
    BottleInterceptor(agent, mod.HTTPError).attach('__init__', patched_method_name='add_exception')
