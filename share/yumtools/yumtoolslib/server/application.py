# -*- coding: utf-8 -*-

import Queue
from yumtoolslib.singleton import Singleton

class Application(Singleton):

    def init(self):
        self.queue_cmdproc = Queue.Queue()
        self.queue_createrepo = Queue.Queue()


