# -*- coding: utf-8 -*-

class Singleton(object):
    __instance = None

    def __new__(classtype, *args, **kwargs):
        if classtype != type(classtype.__instance):
            classtype.__instance = object.__new__(classtype, *args, **kwargs)
            classtype.__instance.init()

        return classtype.__instance


    def init(self):
        pass


