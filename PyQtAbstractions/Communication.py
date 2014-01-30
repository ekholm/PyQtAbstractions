# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

"""
This module provides common abstraction for serial based communication
"""

__all__ = []

import sys

import serial

import socket
import re
import uuid
import fcntl

import usb.control
import usb.core
import usb.util
import usb.backend

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Common base class
class CommunicationError(Exception):
    pass

class Base():
    """
    Common base class for communication
    """

    def __init__(self):
        """
        Constructor
        """

        pass

    def write(*args):
        print("required function 'write' not implemented")

    def read(*args):
        print("required function 'read' not implemented")

    def reset(*args):
        print("required function 'reset' not implemented")
        
    def close(self):
        self._dev.close()
        self._dev = None

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# UDP/IP related
class ETH(Base):
    def __init__(self, port, mac):
        Base.__init__(self)

        self.port  = port
        self.mac   = mac

        self._dev = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_IPIP)
        # self._dev = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
	#         self._dev.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        # self._dev = socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM)
        # fcntl.ioctl(self._dev.fileno, self._dev.SIOCGIFHWADDR)
        self._dev.bind((self.port, socket.IPPROTO_IPIP))
        # self._dev.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 0)
        # fcntl.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def write_ctrl(self, cmd, value, index, data = []):
        src = [int(x, 16) for x in re.findall('..', '{:012x}'.format(uuid.getnode()))]
        dst = [int(x) for x in self.mac.split(':')]
        data =  src + dst + [
            0x00, # ethernet frame type
            6 + len(data),  # len
            0x00, 0x00,     # header
            0x00, 0x00, 0x00, cmd] + data

        data =''.join([chr(item) for item in data])
        self._dev.sendto(data, (self.port, 0))

        print('write_ctrl', cmd, value, index, data)

    def read_ctrl(self, cmd, value, index, length):
        print('read_ctrl', cmd, value, index, length)

    def write(self, data):
        print('write')
        self._dev.send(handly_crafted_packet)

    def read(self, len = 65536, timeout = 0):
        print('read data')
        (data, _) = self._dev.recvfrom(len)
        print(data)
        return data

    def reset(self):
        pass

    def __str__(self):
        return '{:s}:{:s} @ fd:{:d}'.format(self.port, self.mac, self._dev.fileno())

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# UDP/IP related
class IP(Base):
    def __init__(self, ip, port):
        Base.__init__(self)

        self.ip        = ip
        self.port      = port

    def __str__(self):
        return '{:s}:{:d} @ fd:{:d}'.format(self.ip, self.port, self._dev.fileno())

class UDP(IP):
    def __init__(self, ip, port):
        IP.__init__(self, ip, port)
        self._dev = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # , socket.IPPROTO_UDP)
        self._dev.settimeout(.2)

    def write(self, data):
        """
        """

        # print [ord(a) for a in data]
        if sys.version_info.major == 3:
            if type(data) == list:
                data = bytearray(x for x in data)
        else:
            data =''.join([chr(item) for item in data])

        self._dev.sendto(data, (self.ip, self.port))

    def read(self, len = 65536, timeout = 0):
        (data, _) = self._dev.recvfrom(len)

        return data

    def reset(self):
        pass

class UDPSrv(IP):
    def __init__(self, ip, port):
        IP.__init__(self, ip, port)
        self._dev = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # , socket.IPPROTO_UDP)
        self._dev.bind(('', self.port))
        self._dev.setblocking(True)

        (_, self.port) = self._dev.getsockname()

    def read(self, len = 65536, timeout = 0):
        (data, _) = self._dev.recvfrom(len)

        return data

    def reset(self):
        pass

class TCP(IP):
    def __init__(self, ip, port, blocking = True):
        IP.__init__(self, ip, port)
        self._dev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._dev.connect((ip, port))
        self._dev.setblocking(blocking)

    def write(self, data):
        if sys.version_info.major == 3:
            if type(data) == list:
                data = bytearray(x for x in data)
        else:
            data =''.join([chr(item) for item in data])

        totsent = 0
        size = len(data)
        # USE sendall instead
        while totsent < size:
            sent = self._dev.send(data[totsent:])

            if sent == 0:
                raise RuntimeError("socket connection broken")
            totsent += sent

        return totsent

    def read(self, size = 65536, timeout = 0):
        data = []
        while len(data) < size:
            tmp = self._dev.recv(size - len(data))

            if tmp == '':
                raise RuntimeError("socket connection broken")
            data += tmp

        return data

    def reset(self):
        pass

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# USB related
USBCoreError = usb.core.USBError

class USBError(CommunicationError):
    pass

class USB(Base):
    def __init__(self, vid, pid, alt_iface = 0, raw = False):
        """
        Constructor that retrives the selected USB device
        """

        Base.__init__(self)

        self._dev = usb.core.find(idVendor = vid, idProduct = pid)

        if not self._dev:
            # TODO: throw exception instead ExceptionNoDevice
            raise USBError("No device found")

        self._alt_iface = alt_iface
        self._startUSB(raw)

    def _startUSB(self, raw = False):
        """
        Internal method that starts the USB device communication and
        initializes the interfaces and end-points
        """

        try:
            print("Found device 0x{:04x}:0x{:04x} at {:s}:{:s}".format(self._dev.idVendor,
                                                                       self._dev.idProduct,
                                                                       self._dev.bus,
                                                                       self._dev.address))
        except:
            print("Found device 0x{:04x}:0x{:04x}".format(self._dev.idVendor,
                                                          self._dev.idProduct))

        # Force it into a known state and reset it
        try:
            if not raw:
                self._dev.set_configuration()
        except Exception as e:
            print(str(e))
            # TODO: alert parent that we are dying
            # self._loop.quit()
            sys.exit()

        # self._dev.reset()
        # print(self._dev._ctx.backend)

        # Get the current active configuration set
        self._cfg = self._dev.get_active_configuration()

        self._ifaces = []
        for i in self._cfg:
            self._ifaces += [i]
            # self.printIface(i)

        # Get its interface
        self._iface = self._ifaces[self._alt_iface] # self._cfg[(0, 0)]
        if not raw:
            self._dev.set_interface_altsetting(interface = 0, alternate_setting = self._alt_iface)

        #self.printDevice()
        #self.printConfig()
        #self.printIface()

        # retrieve the endpoints
        self._ep = []
        self._ep_in  = None
        self._ep_out = None
        for i in range(self._iface.bNumEndpoints):
            ep   = self._iface[i]
            # self.printEndPoint(ep)
            self._ep += [ep]

            attr = ep.bmAttributes
            if usb.util.endpoint_type(attr) == usb.util.ENDPOINT_TYPE_CTRL:
                print("Found CTRL Endpoint")
            elif usb.util.endpoint_type(attr) == usb.util.ENDPOINT_TYPE_ISO:
                print("Found ISO Endpoint")
            elif usb.util.endpoint_type(attr) == usb.util.ENDPOINT_TYPE_BULK:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    print("Found BULK Endpoint out @ {:d}".format(ep.bEndpointAddress))
                    self._ep_out = ep
                else:
                    print("Found BULK Endpoint in @ {:d}".format(ep.bEndpointAddress))
                    self._ep_in  = ep

            elif usb.util.endpoint_type(attr) == usb.util.ENDPOINT_TYPE_INTR:
                print("Found INTR Endpoint")
            else:
                pass

        # print(self)

    def restart(self):
        """
        Restarts the USB communication
        """

        usb.util.dispose_resources(self._dev)
        self._startUSB()
        self._dev.reset()

    def write(self, data):
        """
        Write the data to the data end-point
        """

        self._ep_out.write(data)

    def read(self, len = 65536, timeout = 0):
        """
        Read a given number of data from tha data in end-point

        """
        read = self._ep_in.read(len, timeout = timeout)
        return read

    def reset(self):
        self._dev.reset()

    def write_ctrl(self, cmd, value, index, data = None):
        """
        Write data over the device control channel
        """

        reqType = usb.util.build_request_type(usb.util.CTRL_OUT,
                                              usb.util.CTRL_TYPE_VENDOR,
                                              usb.util.CTRL_RECIPIENT_DEVICE)

        self._dev.ctrl_transfer(reqType, cmd, wValue = value, wIndex = index, data_or_wLength = data)
        # ctrl_transfer(self, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength = None, timeout = None)

    def _read_ctrl(self, cmd, value, index):
        """
        Read data from the device control channel
        """

        reqType = usb.util.build_request_type(usb.util.CTRL_IN,
                                              usb.util.CTRL_TYPE_VENDOR,
                                              usb.util.CTRL_RECIPIENT_DEVICE)
        return self._dev.ctrl_transfer(reqType, cmd, wValue = value, wIndex = index)

    def read_ctrl(self, cmd, value, index, len):
        """
        Read data from the device control channel
        """

        reqType = usb.util.build_request_type(usb.util.CTRL_IN,
                                              usb.util.CTRL_TYPE_VENDOR,
                                              usb.util.CTRL_RECIPIENT_DEVICE)
        return self._dev.ctrl_transfer(reqType, cmd, wValue = value, wIndex = index,
                                       data_or_wLength = len)

    # ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
    # printing
    def __str__(self):
        """
        Returns a string representation of the USB connection
        """

        desc = "USB device:\n"
        desc += "\t{:04x}:{:04x}".format(self._dev.idVendor,
                                         self._dev.idProduct)
        try:
            desc += " at {:s}:{:s}\n".format(self._dev.bus,
                                             self._dev.address)
        except:
            pass

        desc += "\t{:s} {:s}\n".format(usb.util.get_string(self._dev, 1024, 1),
                                       usb.util.get_string(self._dev, 1024, 2))
        desc += "\tit has {:d} interfaces (with {:d} variants), which has {:d} endpoints".format(
            self._cfg.bNumInterfaces,
            len(self._ifaces),
            self._iface.bNumEndpoints)

        return desc

    def printDevice(self):
        """
        Print USB device information
        """

        self.printUsb("Device", self._dev, usb.backend.libusb10._libusb_device_descriptor._fields_)

    def printConfig(self):
        """
        Print USB configuration information
        """

        self.printUsb("Config", self._cfg, usb.backend.libusb10._libusb_config_descriptor._fields_)

    def printIface(self, iface = None):
        """
        Print USB interface information
        """

        if not iface:
            iface = self._iface
        self.printUsb("Interface", iface, usb.backend.libusb10._libusb_interface_descriptor._fields_)

    def printEndPoint(self, ep):
        """
        Print USB end-point information
        """

        self.printUsb("Endpoint", ep, usb.backend.libusb10._libusb_endpoint_descriptor._fields_)

    def printUsb(self, unit, dev, fields):
        """
        Print USB information
        """

        print("{:s}:".format(unit))
        for (p, _) in fields:
            if hasattr(dev, p):
                val = getattr(dev, p)
                print("\t{:s} {:d} 0x{:x}".format(p, val, val))

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Serial port
class SerialError(CommunicationError):
    pass

class Serial(Base):
    """
    Base class for serial port communication
    """

    def __init__(self, port, speed = 9600):
        """
        Constructor
        """

        Base.__init__(self)

        try:
            self._dev = serial.Serial(
                # port     = port,
                baudrate = speed,
                bytesize = serial.EIGHTBITS,
                parity   = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                timeout = 0.5)

            self._dev.port = port
            self._dev.open()

        except Exception as e:
            raise SerialError(e)

        # print(self)

    def write(self, data):
        """
        Write data to serial port
        """

        if type(data) == list:
            tmp = ''
            for d in data:
                tmp += '{:d}'.format(d)
            # print len(data), len(tmp), data
            data = tmp

        if sys.version_info.major == 3:
            data = bytearray(ord(x) for x in data)

        return self._dev.write(data)

    def read(self, len = 1):
        """
        Read data from serial port
        """

        return self._dev.read(len)

    def reset(self):
        pass

    def readline(self, eol = '\n'):
        """
        Read a line of data from serial port
        """

        data = ""
        ch   = chr(0)
        while ch not in eol:
            ch = self._dev.read(1)
            if sys.version_info.major == 3:
                ch = ch.decode("utf-8")
            data += ch

        return data

    def __str__(self):
        """
        Return a string represenation of the serial port connection
        """

        desc = "Serial port:\n"
        desc += "\t{:s}".format(self._dev.name)
        desc += "\t{:d} @ {:d}{:s}{:d}".format(self._dev.baudrate,
                                               self._dev.bytesize,
                                               self._dev.parity,
                                               self._dev.stopbits)

        return desc

class RawSerial(Serial):
    def write(self, data):
        """
        Write data to serial port
        """

        if type(data) == list:
            data = bytearray(x for x in data)

        return self._dev.write(data)
