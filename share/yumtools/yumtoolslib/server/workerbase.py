# -*- coding: utf-8 -*-

import threading
import time
from yumtoolslib import config
from yumtoolslib.server import application

class WorkerBase(threading.Thread):

    def __init__(self):
        super(WorkerBase, self).__init__()
        self.is_running = True
        self.loop_delay = 1
        self.daemon = True
        self.cfg = config.ServerConfig()
        self.app = application.Application()
        self.init()

    def init(self): pass

    def work(self): pass

    def run(self):
        self.is_running = True
        while self.is_running:
            self.work()
            time.sleep(self.loop_delay)

    def stop(self):
        self.is_running = False


