# -*- coding: utf-8 -*-

import os
import re
import md5

re_match_package_name = re.compile(r'^(.*)-([\d\.]+)-(\d+)\.el(\d+)\.(noarch|x86_64|i386)\.rpm$')
re_valid_package_name = re.compile(r'^[\w\-_\.]+$')
re_valid_version = re.compile(r'^\d[\d\.\-]*$')

def getPackageInfos(pkg_name):
    pkg_name = os.path.split(pkg_name)[1]
    rlt = re_match_package_name.findall(pkg_name)
    if len(rlt) == 0:
        return None
    else:
        rlt = rlt[0]
        return {
                "package_name": rlt[0],
                "version": rlt[1],
                "release": rlt[2],
                "os_version": rlt[3],
                "arch": rlt[4]
                }


def passwordHash(pwd):
    hash_obj = md5.new()
    hash_obj.update(pwd)
    hash_obj.update(hash_obj.hexdigest()+"MX")
    return hash_obj.hexdigest().upper()

def validPackagename(s):
    mth = re_valid_package_name.match(s)
    return mth is not None

def validVersion(s):
    mth = re_valid_version.match(s)
    return mth is not None


