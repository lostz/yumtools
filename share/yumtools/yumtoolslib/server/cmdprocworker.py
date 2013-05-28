# -*- coding: utf-8 -*-

import os
import sys
import stat
import time
import shutil
import tempfile
import md5
import subprocess
import ldap
import smtplib
from email.mime.text import MIMEText
from yumtoolslib.server import workerbase
from yumtoolslib import io
from yumtoolslib import net
from yumtoolslib import utils
from yumtoolslib import config
from yumtoolslib.server.yummail import mail.sendMail

MAIL_SUBJECT_TEMPLATE = u"[YumServer] %s %s %s-%s-%s.el%s.%s.rpm %s %s"

class CmdprocWorker(workerbase.WorkerBase):
    operator_name = ""

    def init(self):
        self.loop_delay = 0

    def work(self):
        # get socket object
        skt = None
        try:
            skt = self.app.queue_cmdproc.get(timeout=10)
        except:
            return

        is_succ = True
        skt, peer = skt
        skt = net.SafeTcp(skt)
        io.debug("cmdproc worker", "new client: %s" % str(peer))

        try:
            # check auth
            if is_succ:
                is_succ, resp = self.checkAuth(skt)
                skt.sendPdu(resp)

            io.debug('TRACE', '验证通过')
            # dispatch
            if is_succ:
                is_succ, resp = self.dispatch(skt)
                skt.sendPdu(resp)
        except Exception, _ex:
            is_succ = False
            io.error("cmdproc worker", str(_ex))
        finally:
            skt.close()


    # TODO: ldap
    def checkAuth(self, skt):
        pdu = skt.recvPdu()
        if not isinstance(pdu, net.AuthPdu):
            io.error("cmdproc worker", "pdu is not a AuthPdu instance")
            return False, self._makeResponsePdu(net.PDU_ERROR_AUTH_FAIL, "permission denied, please try later.")

        username = pdu.get("username")
        password = pdu.get("password")
        self.operator_name = username

        io.debug("cmdproc worker", "username=%s, password=%s" % (username, password))
        print self.cfg.auth_method 
        if self.cfg.auth_method == "admin_list":
            if not self.cfg.admin_list.has_key(username) or self.cfg.admin_list[username] != password:
                return False, self._makeResponsePdu(net.PDU_ERROR_AUTH_FAIL, "permission denied, please try later.")
        elif self.cfg.auth_method == "ldap":
            try:
                if password == "":
                    raise ldap.LDAPError
                ldap_conn   = ldap.open("qunarldap.corp.qunar.com")
                ldap_conn.simple_bind_s("%s@qunarservers.com" % username, password)
                pass
            except Exception, _ex:
                return False, self._makeResponsePdu(net.PDU_ERROR_AUTH_FAIL, "permission denied, please try later.")
        else:
            io.error('cmdproc worker', "server auth module not found.")
            return False, self._makeResponsePdu(net.PDU_ERROR_AUTH_FAIL, "server auth module not found.")

        return True, self._makeResponsePdu(net.PDU_ERROR_SUCCESSED, "login successed!")

    def dispatch(self, skt):
        pdu = skt.recvPdu()
        if pdu.commandid.name == "UPLOAD_INFO":
            return self.procUpload(skt, pdu)
        elif pdu.commandid.name == "SETBRANCH":
            return self.procSetbranch(skt, pdu)
        elif pdu.commandid.name == "REMOVE":
            return self.procRemove(skt, pdu)
        else:
            io.error('cmdproc worker', 'command not supported!')
            self._makeResponsePdu(net.PDU_ERROR_ATK, "package name is not a valid value.")
            return False, self._makeResponsePdu(net.PDU_ERROR_ATK, "command not supported!")

    def procUpload(self, skt, first_pdu):
        io.debug('upload', 'start upload command')
        pdu = first_pdu
        # check package_name
        package_name = pdu.get("package_name")
        if not utils.isValidPackageName(package_name):
            return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "package name is not a valid value.")
        # check version
        version = pdu.get("version")
        if not utils.isValidVersion(version):
            return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "version is not a valid value.")
        # check release
        release = pdu.get("release")
        # check os_version
        os_version = pdu.get("os_version")
        if os_version not in self.cfg.os_version_list:
            return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "os version not a valid value.")
        # check arch
        arch = pdu.get("arch")
        if arch not in self.cfg.arch_list:
            return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "arch not a valid value.")
        # check file_size
        file_size = pdu.get("file_size")
        if file_size > 1024 * self.cfg.max_file_size:
            return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "file size is out of maximum value")

        # generate dist file name
        dest_file_name = self._makePackageFullName(self.cfg.upload_branch, release, os_version, arch, package_name, version)
        print dest_file_name
        md5_code = ""

        if os.path.exists(dest_file_name):
            return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "file already exists")

        # send first response
        skt.sendPdu(self._makeResponsePdu(net.PDU_ERROR_SUCCESSED, "package meta-data check is complete."))
        with tempfile.NamedTemporaryFile('wb+') as temp_file:
            total_binary = 0
            md5_hash = md5.new()
            # recv blocks
            while True:
                pdu = skt.recvPdu()
                if pdu.commandid.name == "UPLOAD_BLOCK":
                    binary = pdu.get('binary')
                    total_binary += len(binary)
                    temp_file.write( binary )
                    md5_hash.update( binary )
                    if total_binary > file_size:
                        return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "denied!")
                    skt.sendPdu(self._makeResponsePdu(net.PDU_ERROR_SUCCESSED, ""))
                elif pdu.commandid.name == "UPLOAD_END":
                    # check md5
                    md5_code = pdu.get("md5")
                    break

            temp_file.flush()

            # check md5
            if md5_hash.hexdigest().upper() != md5_code.upper():
                io.error('upload', 'file md5 code is inequality')
                return False, self._makeResponsePdu(net.PDU_ERROR_UPLOADERR, "md5 check error")

            # cp file
            shutil.copy(temp_file.name, dest_file_name)
            os.chmod(dest_file_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH | stat.S_IRGRP)
        #basic_info = os.popen('rpm -qip %s' % dest_file_name).readlines()
        #install_path = os.popen('rpm -qlp %s' % dest_file_name).readlines()

        text = u"RPM包信息\n"
        try:
            reload(sys)
            sys.setdefaultencoding('utf8')
            os.system(u'echo RPM包信息 > /usr/share/yumtools/rpm_basic.info')
            os.system(u'echo 安装信息 > /usr/share/yumtools/rpm_install.info')
            os.system(u'rpm -qip %s > /usr/share/yumtools/rpm_basic.info' % dest_file_name)
            os.system(u'rpm -qlp %s > /usr/share/yumtools/rpm_install.info' % dest_file_name)
            basic_info      = open('/usr/share/yumtools/rpm_basic.info', 'r')
            install_info    = open('/usr/share/yumtools/rpm_install.info', 'r')
            for i in basic_info:
                text = text + i.encode('utf8')
            text = text + u'--------------------------------------------------------\n'
            for i in install_info:
                text = text + i.encode('utf8')
        except Exception, _ex:
            io.error("rpm info error", str(_ex))
            pass
        subject = MAIL_SUBJECT_TEMPLATE % (self.operator_name, u"upload", package_name, version, release, os_version, arch, u"", u"")
        sendMail(config.ServerConfig().mail_sender, config.ServerConfig().mail_receiver, subject, text)


        upload_branch_dirname = self.cfg.branches[self.cfg.upload_branch]
        # put to queue
        self.app.queue_createrepo.put(self._makePackagePath(self.cfg.upload_branch, release, os_version, arch))

        io.log('upload', '%s successed.' % dest_file_name)

        return True, self._makeResponsePdu(net.PDU_ERROR_SUCCESSED, "upload successed!")

    def procSetbranch(self, skt, first_pdu):
        pdu = first_pdu
        # check package_name
        package_name = pdu.get("package_name")
        if not utils.isValidPackageName(package_name):
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "package name is not a valid value.")
        # check version
        version = pdu.get("version")
        if not utils.isValidVersion(version):
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "version is not a valid value.")
        # check release
        release = pdu.get("release")
        # check os_version
        os_version = pdu.get("os_version")
        if os_version not in self.cfg.os_version_list:
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "os version not a valid value.")
        # check arch
        arch = pdu.get("arch")
        if arch not in self.cfg.arch_list:
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "arch not a valid value.")
        # from branch
        from_branch = pdu.get("from_branch")
        # to branch
        to_branch = pdu.get("to_branch")
        if (from_branch not in self.cfg.branches) or (to_branch not in self.cfg.branches):
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "branch name not exists")

        # generate dist file name
        from_file_name = self._makePackageFullName(from_branch, release, os_version, arch, package_name, version)
        dest_file_name = self._makePackageFullName(to_branch, release, os_version, arch, package_name, version)

        if not os.path.exists(from_file_name):
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "file not exists in branch %s" % from_branch)
        if os.path.exists(dest_file_name):
            return False, self._makeResponsePdu(net.PDU_ERROR_SETBRANCHERR, "file already exists in branch %s" % to_branch)


        text = u"设置分支\n"
        subject = MAIL_SUBJECT_TEMPLATE % (self.operator_name, u"setbranch", package_name, version, release, os_version, arch, from_branch, to_branch)
        sendMail(config.ServerConfig().mail_sender, config.ServerConfig().mail_receiver, subject, text)

        # move file
        shutil.move(from_file_name, dest_file_name)

        # put to queue
        self.app.queue_createrepo.put(self._makePackagePath(from_branch, release, os_version, arch))
        self.app.queue_createrepo.put(self._makePackagePath(to_branch, release, os_version, arch))

        return True, self._makeResponsePdu(net.PDU_ERROR_SUCCESSED, "setbranch successed!")

    def procRemove(self, skt, first_pdu):
        pdu = first_pdu
        # check package_name
        package_name = pdu.get("package_name")
        if not utils.isValidPackageName(package_name):
            return False, self._makeResponsePdu(net.PDU_ERROR_REMOVEERR, "package name is not a valid value.")
        # check version
        version = pdu.get("version")
        if not utils.isValidVersion(version):
            return False, self._makeResponsePdu(net.PDU_ERROR_REMOVEERR, "version is not a valid value.")
        # check release
        release = pdu.get("release")
        # check os_version
        os_version = pdu.get("os_version")
        if os_version not in self.cfg.os_version_list:
            return False, self._makeResponsePdu(net.PDU_ERROR_REMOVEERR, "os version not a valid value.")
        # check arch
        arch = pdu.get("arch")
        if arch not in self.cfg.arch_list:
            return False, self._makeResponsePdu(net.PDU_ERROR_REMOVEERR, "arch not a valid value.")
        # branch
        branch = pdu.get("branch")
        if branch not in self.cfg.branches:
            return False, self._makeResponsePdu(net.PDU_ERROR_REMOVEERR, "branch name not exists")

        # generate dist file name
        dest_file_name = self._makePackageFullName(branch, release, os_version, arch, package_name, version)

        if not os.path.exists(dest_file_name):
            io.debug('setbranch', '%s not exists' % dest_file_name)
            return False, self._makeResponsePdu(net.PDU_ERROR_REMOVEERR, "file not exists in branch %s" % branch)

        # move file
        os.unlink(dest_file_name)

        # put to queue
        self.app.queue_createrepo.put(self._makePackagePath(branch, release, os_version, arch))

        text = u"删除分支\n"
        subject = MAIL_SUBJECT_TEMPLATE % (self.operator_name, u"remove", package_name, version, release, os_version, arch, branch, U"")
        sendMail(config.ServerConfig().mail_sender, config.ServerConfig().mail_receiver, subject, text)
        return True, self._makeResponsePdu(net.PDU_ERROR_SUCCESSED, "remove successed!")

    def _makeResponsePdu(self, error_code, msg):
        pdu = net.ResponsePdu()
        pdu.set("error_code", error_code)
        pdu.set("msg", msg)
        return pdu



    def _makePackageName(self, package_name, version, release, os_version, arch):
        return "%s-%s-%d.el%d.%s.rpm" % (package_name, version, release, os_version, arch)

    def _makePackagePath(self, branch, release, os_version, arch):
        return os.path.join(self.cfg.base_dir, self.cfg.branches[branch], str(os_version), arch)

    def _makePackageFullName(self, branch, release, os_version, arch, package_name, version):
        package_name = self._makePackageName(package_name, version, release, os_version, arch)
        package_path = self._makePackagePath(branch, release, os_version, arch)
        return os.path.join(package_path, package_name)


