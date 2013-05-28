# -*- coding: utf-8 -*-

import os
import re
import md5
from pyrpm.rpm import RPM
from pyrpm import rpmdefs

PACKAGE_NAME_FORMAT         = 'package name is not a valid format. format: <package_name>-<package_version>-<release>.el<os_version>.<arch>.rpm'


_re_pattern_format          = '^%s-%s-%s.%s.%s.%s$'
_re_package_name            = r'([\w\-_]+)'
_re_package_version         = r'([\d\.]+)'
_re_package_release         = r'(\d+)'
_re_package_os_version      = r'el(\d+)'
_re_package_arch            = r'(noarch|x86_64|i386)'
_re_package_extension       = r'rpm'

re_match_package_name       = re.compile(_re_pattern_format % (
                                _re_package_name,
                                _re_package_version,
                                _re_package_release,
                                _re_package_os_version,
                                _re_package_arch,
                                _re_package_extension
                            ))
re_valid_package_name       = re.compile(r'^' + _re_package_name + r'$')
re_valid_version            = re.compile(r'^' + _re_package_version + r'$')

def _trimPath(package_name):
    return os.path.split(package_name)[1]

def getPackageInfoByName(package_name):
    package_name = _trimPath(package_name)
    matches      = re_match_package_name.findall(package_name)
    if len(matches) == 0:
        return None
    else:
        matches = matches[0]
        return {
                    "package_name"  : matches[0],
                    "version"       : matches[1],
                    "release"       : matches[2],
                    "os_version"    : matches[3],
                    "arch"          : matches[4]
                }


def getPackageNameFromFile(package_name):
    try:
        rpm = RPM(file(package_name))
        return rpm.filename()
    except Exception, _ex:
        return None


def isPackageAccord(package_name_from_file, **package_infos):
    package_name            = package_infos["package_infos"]["package_name"]
    version                 = package_infos["package_infos"]["version"]
    release                 = package_infos["package_infos"]["release"]
    os_version              = package_infos["package_infos"]["os_version"]
    arch                    = package_infos["package_infos"]["arch"]
    package_name_from_infos = '%s-%s-%s.el%s.%s.rpm' % (package_name, version, release, os_version, arch)
    if cmp(package_name_from_file, package_name_from_infos) != 0:
        return False
    else:
        return True


def getPasswordHash(password):
    hash_password = md5.new()
    hash_password.update(password)
    hash_password.update(hash_password.hexdigest()+"MX")
    return hash_password.hexdigest().upper()


def isValidPackageName(package_name):
    mth = re_valid_package_name.match(package_name)
    return mth is not None


def isValidVersion(version):
    mth = re_valid_version.match(version)
    return mth is not None


