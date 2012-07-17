# -*- coding: utf-8 -*-

import unittest
import random
from yumtoolslib import net

class PduTest(unittest.TestCase):

    def test_pdu_command_id(self):
        self.assertEqual(net.Pdu.commandid.command_id, 0x00000000)
        self.assertEqual(net.ResponsePdu.commandid.command_id, 0x00000001)
        pdu = net.AuthPdu()
        self.assertEqual(pdu.commandid.command_id, 0x10000001)
        self.assertEqual(pdu.commandid.name, "AUTH")

        commandid = net.PduCommandID.getById(0x40000001)
        self.assertEqual(commandid.command_id, 0x40000001)
        self.assertEqual(commandid.name, 'REMOVE')
        self.assertEqual(commandid.cls, net.RemovePdu)

    def test_pdu_stream(self):
        stream = net.PduStream()
        stream.writeInt(100)
        _DD = '\x00\x00\x00\x64'
        self.assertEqual(stream.getvalue(), _DD)
        stream.seek(0)
        self.assertEqual(stream.readInt(), 100)
        stream.writeString("hello\0world!")
        stream.seek(0)
        _DD += '\x00\x00\x00\x0Chello\0world!'
        self.assertEqual(stream.getvalue(), _DD)
        stream.seek(0, 2)
        stream.writeBool(True)
        _DD += '\x01'
        self.assertEqual(stream.getvalue(), _DD)


    def test_pdu(self):
        pdu = net.AuthPdu()
        self.assertEqual(pdu.get("username"), "")
        pdu.set("username", "helloworld")
        self.assertEqual(pdu.get("username"), "helloworld")
        pdu.set("password", "123456")
        self.assertEqual(pdu.get("password"), "123456")
        try:
            pdu.set("password", 12)
            self.assertTrue(False)
        except AssertionError:
            self.assertTrue(True)

        try:
            pdu.get("hello")
            self.assertTrue(False)
        except net.PduException:
            self.assertTrue(True)


