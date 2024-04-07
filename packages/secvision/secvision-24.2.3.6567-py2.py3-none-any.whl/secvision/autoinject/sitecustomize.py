# Copyright (c)
# All Rights Reserved

"""Trick Python into loading the agent.

"""

from __future__ import unicode_literals
import os
import sys

from secvision import basic_json_logger

# patching getargspec for inspect since it got deprecaited from python 3.11
try:
    import inspect
    if sys.version_info[0] == 3 and sys.version_info[1] == 11:
        if not hasattr(inspect, 'getargspec'):
            inspect.getargspec = inspect.getfullargspec
except AttributeError:
    pass

try:
    sys.path.remove(os.path.dirname(__file__))
except ValueError:  # directory not in sys.path
    pass

try:
    import secvision.agent
    if secvision.agent.configure():
        secvision.agent.bootstrap()
except:
    logger = basic_json_logger('secvision.agent')
    logger.exception('Exception in agent startup.')
finally:
    secvision.agent.load_sitecustomize()
