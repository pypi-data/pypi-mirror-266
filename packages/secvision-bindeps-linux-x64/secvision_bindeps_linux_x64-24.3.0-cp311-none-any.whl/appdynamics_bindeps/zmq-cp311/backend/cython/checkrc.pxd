# 2022-07-07, Cisco Systems, Inc.
from libc.errno cimport EINTR, EAGAIN
from cpython cimport PyErr_CheckSignals

from .libzmq cimport zmq_errno, ZMQ_ETERM


cdef inline int _check_rc(int rc) except -1:
    """internal utility for checking zmq return condition

    and raising the appropriate Exception class
    """
    cdef int errno = zmq_errno()
    PyErr_CheckSignals()
    if rc == -1: # if rc < -1, it's a bug in libzmq. Should we warn?
        if errno == EINTR:
            from appdynamics_bindeps.zmq.error import InterruptedSystemCall
            raise InterruptedSystemCall(errno)
        elif errno == EAGAIN:
            from appdynamics_bindeps.zmq.error import Again
            raise Again(errno)
        elif errno == ZMQ_ETERM:
            from appdynamics_bindeps.zmq.error import ContextTerminated
            raise ContextTerminated(errno)
        else:
            from appdynamics_bindeps.zmq.error import ZMQError
            raise ZMQError(errno)
    return 0
