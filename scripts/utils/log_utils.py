# -*- coding: utf-8 -*-
import logging
import os

__author__ = 'Kevin Sun <sun-w@klab.com>'


def init(base_dir):
    global logger
    logger = logging.getLogger("sdk_tools")
    logger.setLevel(logging.DEBUG)
    log_file = base_dir + "/log/sdk_tools.log"
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = logging.FileHandler(log_file, "w", "UTF-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)


def info(msg, *args):
    if len(msg) <= 0:
        return
    logger.info(msg, *args)


def debug(msg, *args):
    if len(msg) <= 0:
        return
    logger.debug(msg, *args)


def warning(msg, *args):
    if len(msg) <= 0:
        return
    logger.warning(msg, *args)


def error(msg, *args):
    if len(msg) <= 0:
        return
    logger.error(msg, *args)
