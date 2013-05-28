# -*- coding: utf-8 -*-

import unittest
import random
from yumtoolslib import utils

class UtilsTest(unittest.TestCase):

    def test_valid_package_name(self):
        self.assertTrue(utils.validPackagename('hello'))
        self.assertTrue(utils.validPackagename('test-python27'))
        self.assertFalse(utils.validPackagename('test/python27'))
        self.assertFalse(utils.validPackagename('test?python27'))
        self.assertFalse(utils.validPackagename('test\0python27'))

    def test_valid_version(self):
        self.assertFalse(utils.validVersion('test-python27'))
        self.assertFalse(utils.validVersion('test'))
        self.assertFalse(utils.validVersion('-.'))
        self.assertTrue(utils.validVersion('1-.'))
        self.assertFalse(utils.validVersion(' 1-.'))
        self.assertFalse(utils.validVersion('1 '))


