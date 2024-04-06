import threading
import time

from sciveo.common.tools.logger import *
from sciveo.common.tools.synchronized import ListQueue
from sciveo.api.upload import APIFileUploader


class DaemonBase:
  def __init__(self, num_threads=1, period=0):
    self.is_running = False
    self.is_started = False
    self.num_threads = num_threads
    self.period = period

  def start(self):
    if self.is_started:
      return

    self.is_running = True
    self.is_started = True

    self.threads = []
    for i in range(self.num_threads):
      T = threading.Thread(target = self.safe_run)
      T.setDaemon(True)
      T.start()
      self.threads.append(T)

  def stop(self):
    self.is_running = False

  def finalise(self):
    pass

  def join(self):
    for i in range(self.num_threads):
      self.threads[i].join()

  def loop(self):
    pass

  def run(self):
    while(self.is_running):
      try:
        self.loop()
      except Exception as e:
        error(type(self).__name__, e)
      time.sleep(self.period)

  def safe_run(self):
    try:
      self.run()
    except Exception as e:
      error(type(self).__name__, e)


class TasksDaemon(DaemonBase):
  current = None
  queue = ListQueue("tasks")

  def loop(self):
    task = TasksDaemon.queue.pop()
    task()


def __upload_content__(content_type, local_path, parent_guid):
  TasksDaemon.queue.push(APIFileUploader(content_type, local_path, parent_guid))