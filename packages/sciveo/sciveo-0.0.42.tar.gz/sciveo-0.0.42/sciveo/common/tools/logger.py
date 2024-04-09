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
import logging
import threading


log_min_level = os.environ.setdefault('SCI_LOG_MIN_LEVEL', "DEBUG")

def get_logger(name):
  logger = logging.getLogger(name)

  if not logger.handlers:
    logger.setLevel(logging.getLevelName(log_min_level))
    formatter = logging.Formatter('%(asctime)s [%(thread)d] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

  return logger



SCIVEO_LOGGER_NAME = "sciveo-log"

def debug(*args):
  get_logger(SCIVEO_LOGGER_NAME).debug(args)
def info(*args):
  get_logger(SCIVEO_LOGGER_NAME).info(args)
def warning(*args):
  get_logger(SCIVEO_LOGGER_NAME).warning(args)
def error(*args):
  get_logger(SCIVEO_LOGGER_NAME).error(args)
def critical(*args):
  get_logger(SCIVEO_LOGGER_NAME).critical(args)