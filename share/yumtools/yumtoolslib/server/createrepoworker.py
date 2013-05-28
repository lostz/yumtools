# -*- coding: utf-8 -*-

import os
import subprocess
import threading
from yumtoolslib.server import workerbase
from yumtoolslib import io

def writeWorker(output_filename, stream):
    fp = open(output_filename, "a+")
    while True:
        a = stream.read(1)
        if a == "":
            break
        fp.write(a)
        fp.flush()
    fp.close()


class CreaterepoWorker(workerbase.WorkerBase):

    def init(self):
        self.loop_delay = 0

    def work(self):
        repo_path = None
        try:
            repo_path = self.app.queue_createrepo.get(timeout=5)
        except:
            pass
        if repo_path is None:
            return

        try:
            self.doCommand("/usr/bin/createrepo", "-d", "-s", "md5", repo_path)
        except Exception, _ex:
            io.error("create repo worker", str(_ex))


    def doCommand(self, *args):
        rlt = subprocess.Popen(args,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)

        thread_out = threading.Thread(target=writeWorker, args=(self.cfg.stdout_file, rlt.stdout))
        thread_err = threading.Thread(target=writeWorker, args=(self.cfg.stderr_file, rlt.stderr))

        thread_out.start()
        thread_err.start()

        thread_out.join()
        thread_err.join()

        rlt.wait()




