# -*- coding: utf-8 -*-

from yumtoolslib import net
from yumtoolslib import io

class YumtoolsClient(object):

    def __init__(self):
        self.skt = net.SafeTcp()

    def connect(self, host, port):
        try:
            self.skt.connect(host, port)
        except:
            return False
        return True

    def login(self, user_name, password):
        pdu = net.AuthPdu()
        pdu.set("username", user_name)
        pdu.set("password", password)
        try:
            self.skt.sendPdu(pdu)
            if not self._recvResponse():
                return False
        except Exception, _ex:
            io.error('', str(_ex))
            return False

        return True

    def _recvResponse(self, output=True):
        try:
            pdu = self.skt.recvPdu()
            return self._parseResponse(pdu, output)
        except:
            io.error('', 'response message receive error.')
            return False

    def _parseResponse(self, response, output=True):
        error_code = response.get("error_code")
        msg = response.get("msg")
        if error_code == net.PDU_ERROR_SUCCESSED:
            if output:
                io.log('', msg)
            return True
        else:
            if output:
                io.error('0x%08X' % error_code, msg)
            return False

    def invokeRemote(self, pdu, output=True):
        try:
            self.skt.sendPdu(pdu)
        except:
            io.error('', 'pdu send error.')
            return False

        return self._recvResponse(output)

