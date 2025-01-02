# -*- coding: utf-8 -*-
import threading
from utils import conf_utils,cli_utils
from click import secho
import traceback
import sys

if conf_utils.is_py_env_2():
    import Queue as queue
else:
    import queue

__author__ = 'Kevin Sun <sun-w@klab.com>'

has_error = False

def run_all_channels(channels, thread_num=1):
    if len(channels) < thread_num:
        thread_num = len(channels)
    task_queue = queue.Queue()
    for channel in channels:
        task_queue.put(channel, True)
    for i in range(thread_num):
        packing_worker = PackingWorker(task_queue, i)
        packing_worker.start()
    # blocked ,resume when all tasks have processed
    task_queue.join()
    if has_error:
        secho("[Error] have something error", fg='red')
        sys.exit(-1)
    else:
        secho("[OK] packing done", fg='green')


class PackingWorker(threading.Thread):
    def __init__(self, task_queue, thread_index):
        threading.Thread.__init__(self)
        self.thread_index = thread_index
        self.daemon = True
        self.task_queue = task_queue
        self.suc_num = 0
        self.fail_num = 0

    def run(self):
        while True:
            try:
                if self.task_queue.empty():
                    break
                # this method will block
                channel = self.task_queue.get()
                ret = channel.pack()
                if ret:
                    self.fail_num += 1
                    sys.exit(-1)
                else:
                    self.suc_num += 1
            except Exception as e:
                traceback.print_exc()
                secho("[Exception]" + str(e), fg='red')
                global has_error
                has_error = True
            finally:
                self.task_queue.task_done()
