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
import json
from urllib import request, parse
from urllib.error import HTTPError

from sciveo.common.tools.logger import *


class APIRemoteClient:
  def __init__(self, base_url=None, ver=1):
    if base_url is None:
      base_url = os.environ.get("SCIVEO_API_BASE_URL", "https://sciveo.com")
    self.base_url = f"{base_url}/api/v{ver}/"
    self.headers = { "Auth-Token": os.environ.get('SCIVEO_SECRET_ACCESS_KEY', "") }
    debug(type(self).__name__, f"base url: {self.base_url}")

  def POST_SCI(self, content_type, data, timeout=30):
    return self.POST(f"sci/{content_type}/", data, timeout)

  def POST(self, url, data, timeout=30):
    url = f"{self.base_url}{url}"
    result = False
    try:
      data = parse.urlencode(data).encode("utf-8")
      # debug("POST", url, data)
      resp = request.urlopen(request.Request(url, data=data, headers=self.headers), timeout=timeout)
      result = json.loads(resp.read())
      # debug("POST result", result)
    except HTTPError as e:
      error(e, url, data)
    except Exception as e:
      error(e, url, data)
    return result

  def GET(self, url, timeout=30):
    url = f"{self.base_url}{url}&auth_token={os.environ['SCIVEO_SECRET_ACCESS_KEY']}"
    result = False
    try:
      # debug("GET", url)
      resp = request.urlopen(request.Request(url, headers=self.headers), timeout=timeout)
      result = json.loads(resp.read())
      # debug("GET", resp.status, result)
    except HTTPError as e:
      error(e, url)
    except Exception as e:
      error(e, url)
    return result
