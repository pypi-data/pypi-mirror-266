# Copyright (c)
# All Rights Reserved

from __future__ import unicode_literals
import secvision.agent

from secvision.agent.interceptor.frameworks.wsgi import WSGIMiddleware


def composite_factory(loader, global_conf, target, **local_conf):
    target = loader.get_app(target, global_conf=global_conf)

    try:
        if not secvision.agent.configure(local_conf):
            return target

        return WSGIMiddleware(application=target)
    except:
        return target
