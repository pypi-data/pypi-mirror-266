#
# Pavlin Georgiev, Softel Labs
#
# This is a proprietary file and may not be copied,
# distributed, or modified without express permission
# from the owner. For licensing inquiries, please
# contact pavlin@softel.bg.
#
# 2024
#

import unittest
import numpy as np

from sciveo.common.tools.logger import *
from sciveo.monitoring.monitor import *


class TestMonitoring(unittest.TestCase):
  def test_cpu(self):
    m = BaseMonitor()
    m.get_cpu_usage()
    print(m.data)

    self.assertTrue("usage_per_core" in m.data["CPU"])
    self.assertTrue("usage" in m.data["CPU"])
