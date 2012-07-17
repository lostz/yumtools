# -*- coding: utf-8 -*-

import StringIO
import socket
import struct

PDU_ERROR_SUCCESSED =       0x00000000
PDU_ERROR_AUTH_FAIL =       0x00000001
PDU_ERROR_UPLOADERR =       0x10000002
PDU_ERROR_SETBRANCHERR =    0x10000002
PDU_ERROR_REMOVEERR =       0x10000003
PDU_ERROR_ATK =             0x20000001

PDU_CRYPT_NONE  =   0x00000000
PDU_CRYPT_ZIP   =   0x00000001

class NetException(Exception): pass
class PduStreamException(NetException): pass
class PduException(NetException): pass
class SafeTcpException(Exception): pass

#{{{ Pdu command definition

class PduCommandID(object):

    _cached_id = {}
    _cached_name = {}

    def __init__(self, command_id, name, cls):
        self.command_id = command_id
        self.name = name
        self.cls = cls
        cls.commandid = self
        PduCommandID.setCommand(command_id, name, self)

    @classmethod
    def getById(cls, cmd_id):
        if not PduCommandID._cached_id.has_key(cmd_id):
            return None
        return PduCommandID._cached_id[cmd_id]

    @classmethod
    def getByName(cls, name):
        if not PduCommandID._cached_name.has_key(name):
            return None
        return PduCommandID._cached_name[name]

    @classmethod
    def setCommand(cls, cmd_id, name, pcid_obj):
        assert(isinstance(pcid_obj, PduCommandID))
        PduCommandID._cached_id[cmd_id] = pcid_obj
        PduCommandID._cached_name[name] = pcid_obj

#}}}

#{{{ Pdu stream

class PduStream(StringIO.StringIO):

    def writeInt(self, i):
        self.write(struct.pack('>I', i))

    def readInt(self):
        if self.len < (self.tell() + 4):
            raise PduStreamException("out of bounds.")
        data = self.read(4)
        return struct.unpack('>I', data)[0]

    def writeString(self, data):
        length = len(data)
        self.writeInt(length)
        self.write(data)

    def readString(self):
        length = self.readInt()
        if self.len < (self.tell() + length):
            raise PduStreamException("out of bounds.")
        s = self.read(length)
        return s

    def writeBool(self, b):
        if b == True:
            self.write('\x01')
        elif b == False:
            self.write('\x00')

    def readBool(self):
        if self.len < (self.tell() + 1):
            raise PduStreamException("out of bounds.")
        data = self.read(1)
        if data == "\x01":
            return True
        elif data == "\x00":
            return False
        else:
            raise PduStreamException("wrong parameter")

#}}}

#{{{ PDU definition

class PduField(object):
    _type = None

    def __init__(self, name, value=None):
        self.name = name
        self.setValue(value)

    def setValue(self, value):
        assert(isinstance(value, self._type))
        self._value = value

    def value(self):
        return self._value

class PduStringField(PduField): _type = str
class PduIntField(PduField): _type = int
class PduBoolField(PduField): _type = bool


# pdu base class
class Pdu(object):

    commandid = None

    def __init__(self):
        self.length = 0
        self.crypt_mode = PDU_CRYPT_NONE
        self._body_fields = {}
        self._seq = []

    def addField(self, field):
        assert(isinstance(field, PduField))
        self._body_fields[field.name] = field
        self._seq.append(field)

    def makeBinary(self):
        # create stream
        stream = PduStream()
        body_stream = PduStream()

        # write body
        for field in self._seq:
            if isinstance(field, PduStringField):
                body_stream.writeString(field.value())
            elif isinstance(field, PduIntField):
                body_stream.writeInt(field.value())
            elif isinstance(field, PduBoolField):
                body_stream.writeBool(field.value())

        # length
        self.length = body_stream.len + 12
        stream.writeInt(self.length)
        # commandid
        stream.writeInt(self.commandid.command_id)
        # crypt_mode
        stream.writeInt(self.crypt_mode)
        # body
        stream.write(body_stream.getvalue())

        return stream.getvalue()

    def parseBinary(self, s):
        stream = PduStream(s)
        pdu_length = len(s)
        if pdu_length < 12:
            raise PduException("pdu parse error. [1]")
        length = stream.readInt()
        if length != pdu_length:
            raise PduException("pdu parse error. [2]")
        command_id = stream.readInt()
        if command_id != self.commandid.command_id:
            raise PduException("pdu parse error. [3]")
        crypt_mode = stream.readInt()

        for field in self._seq:
            if isinstance(field, PduStringField):
                field.setValue(stream.readString())
            elif isinstance(field, PduIntField):
                field.setValue(stream.readInt())
            elif isinstance(field, PduBoolField):
                field.setValue(stream.readBool())

        self.length = length
        self.crypt_mode = crypt_mode

        return True

    def set(self, key, value):
        if self._body_fields.has_key(key):
            self._body_fields[key].setValue(value)
        else:
            raise PduException("key %s not found." % key)

    def get(self, key):
        if self._body_fields.has_key(key):
            return self._body_fields[key].value()
        else:
            raise PduException("key %s not found." % key)

    def __str__(self):
        result = StringIO.StringIO()
        result.write("length: %d |" % self.length)
        result.write("commandid: %s |" % self.commandid.name)
        result.write("crypt_mode: %d |" % self.crypt_mode)
        for field in self._seq:
            result.write("<%s>: %s, " % (field.name, str(field.value())))
        return result.getvalue()

# response
class ResponsePdu(Pdu):

    def __init__(self):
        super(ResponsePdu, self).__init__()
        self.addField(PduIntField("error_code", 0))
        self.addField(PduStringField("msg", ""))

# auto
class AuthPdu(Pdu):

    def __init__(self):
        super(AuthPdu, self).__init__()
        self.addField(PduStringField("username", ""))
        self.addField(PduStringField("password", ""))

# upload info
class UploadInfoPdu(Pdu):

    def __init__(self):
        super(UploadInfoPdu, self).__init__()
        self.addField(PduStringField("package_name", ""))
        self.addField(PduStringField("version", ""))
        self.addField(PduIntField("release", 0))
        self.addField(PduIntField("os_version", 0))
        self.addField(PduStringField("arch", ""))
        self.addField(PduIntField("file_size", 0))

# upload block
class UploadBlockPdu(Pdu):

    def __init__(self):
        super(UploadBlockPdu, self).__init__()
        self.addField(PduStringField("binary", ""))

# upload end
class UploadEndPdu(Pdu):

    def __init__(self):
        super(UploadEndPdu, self).__init__()
        self.addField(PduStringField("md5", ""))

# set branch
class SetBranchPdu(Pdu):

    def __init__(self):
        super(SetBranchPdu, self).__init__()
        self.addField(PduStringField("package_name", ""))
        self.addField(PduStringField("version", ""))
        self.addField(PduIntField("release", 0))
        self.addField(PduIntField("os_version", 0))
        self.addField(PduStringField("arch", ""))
        self.addField(PduStringField("from_branch", ""))
        self.addField(PduStringField("to_branch", ""))

# remove
class RemovePdu(Pdu):

    def __init__(self):
        super(RemovePdu, self).__init__()
        self.addField(PduStringField("package_name", ""))
        self.addField(PduStringField("version", ""))
        self.addField(PduIntField("release", 0))
        self.addField(PduIntField("os_version", 0))
        self.addField(PduStringField("arch", ""))
        self.addField(PduStringField("branch", ""))

#}}}

#{{{ Safe Tcp

class SafeTcp(object):

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()

    def safeRecv(self, messageSize):
        message = ""
        while messageSize > 0:
            chunk = self.sock.recv(messageSize)
            if len(chunk) == 0:
                raise SafeTcpException("recv dropped connection")
            messageSize -= len(chunk)
            message += chunk
        return message

    def safeSend(self, msg):
        sent = 0
        while msg:
            i = self.sock.send(msg)
            if i == -1: #发生了错误
                raise SafeTcpException("send dropped connection")
            sent += i
            msg = msg[i:]
        return sent

    def recvPdu(self):
        header = self.safeRecv(12)
        body_length = self._getPduLength(header) - 12
        if body_length < 1:
            raise SafeTcpException("wrong pdu length %d" % body_length)
        if body_length > 10240:
            raise SafeTcpException("wrong pdu length %d (maximum size is 10k)" % body_length)

        body = self.safeRecv(body_length)
        pdu = self._parsePdu(header + body)
        return pdu

    def sendPdu(self, pdu):
        data = pdu.makeBinary()
        return self.safeSend(data)

    def _parsePdu(self, s):
        if len(s) < 12:
            raise SafeTcpException("pdu length must greater than 12 bytes.")

        commandid = struct.unpack('>I', s[4:8])[0]
        commandid_cls = PduCommandID.getById(commandid)
        if commandid_cls is None:
            raise SafeTcpException("wrong command id.")
        pdu = commandid_cls.cls()
        if not pdu.parseBinary(s):
            raise SafeTcpException("wrong pdu format.")
        return pdu



    def _getPduLength(self, s):
        if len(s) < 4:
            raise SafeTcpException("Pdu length error: %d" % len(s))
        result = struct.unpack('>I', s[:4])
        return result[0]

#}}}

PduCommandID(0x00000000,    'NONE',             Pdu)
PduCommandID(0x00000001,    'RESPONSE',         ResponsePdu)
PduCommandID(0x10000001,    'AUTH',             AuthPdu)
PduCommandID(0x20000001,    'UPLOAD_INFO',      UploadInfoPdu)
PduCommandID(0x20000002,    'UPLOAD_BLOCK',     UploadBlockPdu)
PduCommandID(0x20000003,    'UPLOAD_END',       UploadEndPdu)
PduCommandID(0x30000001,    'SETBRANCH',        SetBranchPdu)
PduCommandID(0x40000001,    'REMOVE',           RemovePdu)



