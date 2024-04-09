import threading
import uuid
import copy
import json
import datetime

from sciveo.common.tools.logger import *


class BaseSynchronized:
  def __init__(self, tag=""):
    self.lock_data = threading.Lock()
    if tag:
      tag += "-"
    self._guid = "guid-{}{}-{}".format(tag, datetime.datetime.now().strftime("%Y-%m-%d"), str(uuid.uuid4()).replace("-", ""))

  def guid(self):
    with self.lock_data:
      return self._guid


class ListQueue(BaseSynchronized):
  def __init__(self, tag=""):
    super().__init__(tag)
    self.cv = threading.Condition()
    self.data = []

  def size(self):
    with self.cv:
      return len(self.data)

  def get_data(self):
    with self.cv:
      return copy.deepcopy(self.data)

  def push(self, data):
    with self.cv:
      self.data.append(data)
      self.cv.notify()

  def pop(self, timeout=None):
    with self.cv:
      self.cv.wait_for(predicate=lambda: len(self.data) > 0, timeout=timeout)
      if len(self.data) > 0:
        return self.data.pop(0)
      else:
        raise Exception(f"{type(self).__name__}::POP empty after timeout {timeout}")

