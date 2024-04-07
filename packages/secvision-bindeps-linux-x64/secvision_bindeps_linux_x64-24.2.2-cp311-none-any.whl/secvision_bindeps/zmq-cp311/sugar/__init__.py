# 2022-07-07, Cisco Systems, Inc.
"""pure-Python sugar wrappers for core 0MQ objects."""

# Copyright (C) PyZMQ Developers
# Distributed under the terms of the Modified BSD License.


from secvision_bindeps.zmq.sugar import (
    constants, context, frame, poll, socket, tracker, version
)
from secvision_bindeps.zmq import error

__all__ = ['constants']
for submod in (
    constants, context, error, frame, poll, socket, tracker, version
):
    __all__.extend(submod.__all__)

from secvision_bindeps.zmq.error import *
from secvision_bindeps.zmq.sugar.context import *
from secvision_bindeps.zmq.sugar.tracker import *
from secvision_bindeps.zmq.sugar.socket import *
from secvision_bindeps.zmq.sugar.constants import *
from secvision_bindeps.zmq.sugar.frame import *
from secvision_bindeps.zmq.sugar.poll import *
from secvision_bindeps.zmq.sugar.version import *

# deprecated:
from secvision_bindeps.zmq.sugar.stopwatch import Stopwatch
__all__.append('Stopwatch')
