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

from sciveo.common.tools.formating import format_memory_size

class HardwareInfo:
  def __init__(self):
    self.data = {
      "CPU": {"count": os.cpu_count()},
      "RAM": format_memory_size(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))
    }

    self.get_cpuinfo()

  def __call__(self):
    return self.data

  def get_cpuinfo(self):
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
