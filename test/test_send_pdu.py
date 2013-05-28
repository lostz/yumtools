#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "/usr/share/yumtools")

from yumtoolslib import net


def generic():
    tcp = net.SafeTcp()
    tcp.connect('127.0.0.1', 10030)

    pdu = net.AuthPdu()
    pdu.set("username", "jaypei")
    pdu.set("password", "hello")
    tcp.sendPdu(pdu)

    pdu = net.ResponsePdu()
    pdu.set("error_code", 100)
    pdu.set("msg", "hello world")
    tcp.sendPdu(pdu)

    tcp.close()

def send_login():
    tcp = net.SafeTcp()
    tcp.connect('127.0.0.1', 10030)
    pdu = net.AuthPdu()
    pdu.set("username", "debug")
    pdu.set("password", "debug")
    tcp.sendPdu(pdu)
    response = tcp.recvPdu()
    print response
    pdu = net.UploadInfoPdu()
    pdu.set("package_name", "python27")
    pdu.set("version", "2.7.2")
    pdu.set("release", 1)
    pdu.set("os_version", 6)
    pdu.set("arch", "x86_64")
    pdu.set("file_size", 10240)
    tcp.sendPdu(pdu)
    response = tcp.recvPdu()
    print response
    tcp.close()

if __name__ == '__main__':
    send_login()


