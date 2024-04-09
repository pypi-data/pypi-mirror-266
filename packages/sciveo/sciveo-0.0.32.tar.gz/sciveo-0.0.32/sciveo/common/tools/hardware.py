#
# Pavlin Georgiev, Softel Labs
#
# This is a proprietary file and may not be copied,
# distributed, or modified without express permission
# from the owner. For licensing inquiries, please
# contact pavlin@softel.bg.
#
# 2023
#

import os
import subprocess
import datetime
import uuid
import random
import string

from sciveo.common.tools.logger import *
from sciveo.common.tools.formating import format_memory_size


def new_guid_uuid():
  return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4()).replace("-", "")

def random_token(num_characters):
  characters = string.ascii_letters + string.digits
  return ''.join(random.choices(characters, k=num_characters))

def new_guid(num_characters=32):
  return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + random_token(num_characters)


class HardwareInfo:
  def __init__(self):
    self.data = {
      "CPU": {"count": os.cpu_count()},
      "RAM": format_memory_size(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))
    }

    self.get_cpu()
    self.get_gpu()

  def __call__(self):
    return self.data

  def get_cpu(self):
    list_keys = ["model name", "stepping", "cpu MHz", "cache size", "siblings", "cpu cores", "bogomips"]
    try:
      cpu_info = {}
      with open('/proc/cpuinfo', 'r') as file:
        lines = file.readlines()

      for line in lines:
        if ':' in line:
          key, value = map(str.strip, line.split(':', 1))
          if key in list_keys:
            cpu_info[key] = value

      self.data["CPU"]["info"] = cpu_info
    except Exception:
      return

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
      header = lines[0].split(", ")

      keys = []
      units = {}
      for k in header:
        k_split = k.split(' ')
        key = k_split[0]
        keys.append(key)
        if len(k_split) >= 2:
          units[key] = k_split[1].replace('[', '').replace(']', '')

      for i in range(1, len(lines)):
        line_values = lines[i].split(", ")
        line_data = {}
        for j, value in enumerate(line_values):
          value = value.split(' ')[0]
          line_data[keys[j]] = value
        self.data.setdefault("GPU", [])
        self.data["GPU"].append(line_data)
    except subprocess.CalledProcessError as e:
      pass


if __name__ == "__main__":
  hw = HardwareInfo()
  hw()