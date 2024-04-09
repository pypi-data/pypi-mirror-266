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
import subprocess
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
    self.data["LOG"] = {}
    self.list_logs = []

    self.api = APIRemoteClient()

    # Warmup the psutil cpu usage
    psutil.cpu_percent(interval=0.3, percpu=True)
    initial_cpu_usage = psutil.cpu_percent(interval=None, percpu=True)
    time.sleep(1)

    machine_serial = self.getserial()

    debug(type(self).__name__, "init", machine_serial, "initial_cpu_usage", initial_cpu_usage)

  def __call__(self):
    return self.data

  def loop(self):
    self.get_cpu_usage()
    self.get_memory()
    self.get_gpu()

    self.tail_logs()
    self.data["local_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    api_result = self.api.POST_SCI("monitor", {"data": self.data})

    debug(type(self).__name__, self(), "api_result", api_result)

  def tail_logs(self):
    for log_name, log_path in self.list_logs:
      self.data["LOG"][log_name] = self.tail_file(log_path)[-3:]

  def get_cpu_usage(self):
    usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
    self.data["CPU"]["usage per core"] = usage_per_core
    self.data["CPU"]["usage"] = np.array(usage_per_core).mean()

  def get_memory(self):
    memory = psutil.virtual_memory()
    self.data["RAM"]["used"] = memory.used
    self.data["RAM"]["total"] = memory.total
    self.data["RAM"]["free"] = memory.free
    self.data["RAM"]["print"] = f"total: {format_memory_size(memory.total)} used: {format_memory_size(memory.used)}"

  def getserial(self):
    machine_serial = None
    try:
      with open('/proc/cpuinfo','r') as fp:
        for line in fp:
          if line.startswith('Serial'):
            machine_serial = line[10:26]
    except Exception:
      pass
    if machine_serial is None:
      try:
        machine_serial = socket.gethostname()
      except Exception:
        pass
    if machine_serial is None:
      machine_serial = f"RND-{random_token(8)}"
    self.data["serial"] = machine_serial
    return machine_serial

  def tail_file(self, file_path, block_size=1024):
    result = ["EMPTY"]
    try:
      with open(file_path,'rb') as fp:
        fp.seek(-block_size, os.SEEK_END)
        result = str(fp.read(block_size).rstrip()).split("\\n")
    except Exception as e:
      error(e, "tail_file", file_path)
    return result

  # Currently simple nvidia-smi wrapper impl
  def get_gpu(self):
    try:
      result = subprocess.run(
        [
          'nvidia-smi',
          '--query-gpu=gpu_uuid,gpu_name,index,power.draw,fan.speed,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory,temperature.gpu',
          '--format=csv'
        ],
        capture_output=True, text=True, check=True
      )

      lines = result.stdout.strip().split('\n')
      self.data["GPU"] = {
        "raw_lines": lines
      }
    except Exception as e:
      pass




if __name__ == "__main__":
  mon = BaseMonitor(period=10)
  mon.start()

  while(True):
    time.sleep(30)