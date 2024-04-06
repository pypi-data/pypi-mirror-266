# Copyright (c)
# All Rights Reserved

from __future__ import unicode_literals

from secvision.agent.interceptor.frameworks.wsgi import WSGIMiddleware
application = WSGIMiddleware(set_interceptor=False)
