# 2022-07-07, Cisco Systems, Inc.
# Copyright (C) PyZMQ Developers
# Distributed under the terms of the Modified BSD License.

import sys
from unittest import TestCase

import pytest

class TestImports(TestCase):
    """Test Imports - the quickest test to ensure that we haven't
    introduced version-incompatible syntax errors."""

    def test_toplevel(self):
        """test toplevel import"""
        import secvision_bindeps.zmq

    def test_core(self):
        """test core imports"""
        from secvision_bindeps.zmq import Context
        from secvision_bindeps.zmq import Socket
        from secvision_bindeps.zmq import Poller
        from secvision_bindeps.zmq import Frame
        from secvision_bindeps.zmq import constants
        from secvision_bindeps.zmq import device, proxy
        from secvision_bindeps.zmq import (
            zmq_version,
            zmq_version_info,
            pyzmq_version,
            pyzmq_version_info,
        )

    def test_devices(self):
        """test device imports"""
        import secvision_bindeps.zmq.devices
        from secvision_bindeps.zmq.devices import basedevice
        from secvision_bindeps.zmq.devices import monitoredqueue
        from secvision_bindeps.zmq.devices import monitoredqueuedevice

    def test_log(self):
        """test log imports"""
        import secvision_bindeps.zmq.log
        from secvision_bindeps.zmq.log import handlers

    def test_eventloop(self):
        """test eventloop imports"""
        try:
            import tornado
        except ImportError:
            pytest.skip('requires tornado')
        import secvision_bindeps.zmq.eventloop
        from secvision_bindeps.zmq.eventloop import ioloop
        from secvision_bindeps.zmq.eventloop import zmqstream

    def test_utils(self):
        """test util imports"""
        import secvision_bindeps.zmq.utils
        from secvision_bindeps.zmq.utils import strtypes
        from secvision_bindeps.zmq.utils import jsonapi

    def test_ssh(self):
        """test ssh imports"""
        from secvision_bindeps.zmq.ssh import tunnel

    def test_decorators(self):
        """test decorators imports"""
        from secvision_bindeps.zmq.decorators import context, socket


