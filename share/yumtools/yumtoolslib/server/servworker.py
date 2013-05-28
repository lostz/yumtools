# -*- coding: utf-8 -*-

import socket
from yumtoolslib.server import workerbase

class ServWorker(workerbase.WorkerBase):

    def init(self):
        self.loop_delay = 0

    def work(self):
        t = socket.socket()
        t.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        t.bind((self.cfg.serv_host, self.cfg.serv_port))
        t.listen(5)
        while self.is_running:
            skt = t.accept()
            self.app.queue_cmdproc.put(skt)

        t.close()



