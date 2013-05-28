# -*- coding: utf-8 -*-

import unittest
import random
from yumtoolslib import config

class ConfigTest(unittest.TestCase):

    def test_load_attr(self):
        o = { 'c': { 'd': { 'e': 100 } } }
        # normal
        self.assertEqual(config.loadAttr(o, 'c', 'd', 'e'), 100)
        self.assertEqual(config.loadAttr(o, 'c', 'd'), { 'e':100 })
        # raise error
        self.assertTrue(config.loadAttr(o, 'd', raise_error=False) is None)
        try:
            config.loadAttr(o, 'd')
            self.assertTrue(False)
        except config.LoadConfigError, _ex:
            self.assertTrue(True)

        # default 
        self.assertEqual(config.loadAttr(o, 'c', 'd', 'e', default='hello world'), 100)
        self.assertEqual(config.loadAttr(o, 'c', 'd', 'e2', default='hello world'), 'hello world')
        try:
            self.assertEqual(config.loadAttr(o, 'c', 'd', 'e', default='hello world', type=int), 'hello world')
            self.assertTrue(False)
        except config.LoadConfigError, _ex:
            self.assertTrue(True)
        # no raise error
        self.assertTrue(config.loadAttr(o, 'd', raise_error=False) is None)

        # specify type
        self.assertEqual(config.loadAttr(o, 'c', 'd', 'e', type=int), 100)
        try:
            config.loadAttr(o, 'c', 'd', 'e', type=str)
            self.assertTrue(False)
        except config.LoadConfigError, _ex:
            self.assertTrue(True)


    def test_config_file(self):
        self.assertFalse(config.Config().load('hello'))

        self.assertFalse(config.ClientConfig().load('utest_config_client1.conf'))
        self.assertTrue(config.ClientConfig().load('/etc/yumtools.conf'))

        self.assertFalse(config.ServerConfig().load('utest_config_server1.conf'))
        self.assertTrue(config.ServerConfig().load('/etc/yumtools-serv.conf'))


