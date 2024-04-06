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

import os
import time
import psutil
import numpy as np

from sciveo.common.tools.logger import *
from sciveo.common.tools.daemon import DaemonBase
from sciveo.common.tools.hardware import HardwareInfo
from sciveo.common.tools.formating import format_memory_size
from sciveo.api.base import APIRemoteClient


class BaseMonitor(DaemonBase):
  def __init__(self, period=5):
    super().__init__(period=period)
    self.data = HardwareInfo()()
    self.data.setdefault("CPU", {})
    self.data["RAM"] = {
      "installed": self.data["RAM"]
    }
    psutil.cpu_percent(interval=0.5)
    self.api = APIRemoteClient()

  def __call__(self):
    return self.data

  def loop(self):
    self.get_cpu_usage()
    self.get_memory()
    debug(type(self).__name__, "loop", self())

  def get_cpu_usage(self):
    self.data["CPU"]["usage_per_core"] = psutil.cpu_percent(interval=None, percpu=True)
    # self.data["CPU"]["usage_per_core"] = (np.array(self.data["CPU"]["usage_per_core"]) / 100.0).tolist()
    self.data["CPU"]["usage"] = np.array(self.data["CPU"]["usage_per_core"]).mean()

  def get_memory(self):
    memory = psutil.virtual_memory()
    self.data["RAM"]["total"] = memory.total
    self.data["RAM"]["used"] = memory.used
    self.data["RAM"]["free"] = memory.free
    self.data["RAM"]["print"] = f"total: {format_memory_size(memory.total)} used: {format_memory_size(memory.used)}"


if __name__ == "__main__":
  mon = BaseMonitor(period=10)
  mon.start()

  while(True):
    time.sleep(30)