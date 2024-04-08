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
import datetime
import socket
import psutil
import numpy as np

from sciveo.common.tools.logger import *
from sciveo.common.tools.daemon import DaemonBase
from sciveo.common.tools.hardware import *
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

    self.initial_cpu_usage = psutil.cpu_percent(interval=5, percpu=True)
    cpuserial = self.getserial()

    self.data["logs"] = {}
    self.list_logs = []

    self.api = APIRemoteClient()

    debug(type(self).__name__, "init", cpuserial, "initial_cpu_usage", self.initial_cpu_usage)

  def __call__(self):
    return self.data

  def loop(self):
    self.get_cpu_usage()
    self.get_memory()

    self.tail_logs()
    self.data["local_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    api_result = self.api.POST_SCI("monitor", {"data": self.data})

    debug(type(self).__name__, self(), "api_result", api_result)

  def tail_logs(self):
    for log_name, log_path in self.list_logs:
      self.data["logs"][log_name] = self.tail_file(log_path)[-3:]

  def get_cpu_usage(self):
    if self.initial_cpu_usage is None:
      self.data["CPU"]["usage_per_core"] = psutil.cpu_percent(interval=None, percpu=True)
    else:
      self.data["CPU"]["usage_per_core"] = self.initial_cpu_usage
      self.initial_cpu_usage = None
    # self.data["CPU"]["usage_per_core"] = (np.array(self.data["CPU"]["usage_per_core"]) / 100.0).tolist()
    self.data["CPU"]["usage"] = np.array(self.data["CPU"]["usage_per_core"]).mean()

  def get_memory(self):
    memory = psutil.virtual_memory()
    self.data["RAM"]["total"] = memory.total
    self.data["RAM"]["used"] = memory.used
    self.data["RAM"]["free"] = memory.free
    self.data["RAM"]["print"] = f"total: {format_memory_size(memory.total)} used: {format_memory_size(memory.used)}"

  def getserial(self):
    cpuserial = None
    try:
      with open('/proc/cpuinfo','r') as fp:
        for line in fp:
          if line.startswith('Serial'):
            cpuserial = line[10:26]
    except Exception:
      pass
    if cpuserial is None:
      try:
        cpuserial = socket.gethostname()
      except Exception:
        pass
    if cpuserial is None:
      cpuserial = f"RND-{random_token(8)}"
    self.data["serial"] = cpuserial
    return cpuserial

  def tail_file(self, file_path, block_size=1024):
    result = ["EMPTY"]
    try:
      with open(file_path,'rb') as fp:
        fp.seek(-block_size, os.SEEK_END)
        result = str(fp.read(block_size).rstrip()).split("\\n")
    except Exception as e:
      error(e, "tail_file", file_path)
    return result


if __name__ == "__main__":
  mon = BaseMonitor(period=60)
  mon.start()

  while(True):
    time.sleep(30)