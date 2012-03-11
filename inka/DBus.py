#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

"""
A modules that provides abstractions for the DBus protocol
"""

__all__ = []

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject
import os
import re
import sys
import threading

import inka.__decorators__ as __decorators__

from inka.decorators import on_dbus_signal_send
from inka.decorators import on_dbus_signal_receive
from inka.decorators import dbus_method

Exception = dbus.DBusException

dbus_service = "se.ekholm"
dbus_iface   = dbus_service  + ".iface" 

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Process handling, go daemon
def _doFork():
    """
    This function does a fork and commit suicide in parent. 
    This is useful in daemon creation
    """

    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

def _goDaemon():
    """
    Creates a deamon the Unix standard way.
    """

    _doFork()
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 
    _doFork()

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####

def add_service_arguments(parser):
    """
    Add DBus related arguments to the command line parser for a service
    """

    group = parser.add_argument_group('DBus related')
    group.add_argument('-f', '--force', 
                       dest   = '_dbus_restart', 
                       action = 'store_true', 
                       help   = "Force restart of daemon if running")
    group.add_argument('-e', '--exit', 
                       dest   = '_dbus_kill', 
                       action = 'store_true', 
                       help   = "Kill a runnig daemon")

def add_client_arguments(parser):
    """
    Add DBus related arguments to the command line parser for a client
    """

    group = parser.add_argument_group('DBus related')
    
# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
def findServices(service):
    service = service.split('/')
    path    = '/' + '/'.join(service[1:])
    service = service[0]

    pattern = re.compile(service)
    bus     = dbus.SessionBus() 

    services = []
    for a in bus.list_names():
        if pattern.match(a):
            print bus.get_object(a, path)
            if bus.get_object(a, '/'):
                services += [a]

    return services

def isServiceStarted(service):
    service = service.split('/')
    path    = '/' + '/'.join(service[1:])
    service = service[0]

    bus     = dbus.SessionBus() 

    for a in bus.list_names():
        if service in a:
            return True

    return False


# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# DBUS 
def startService(service, handler, *args, **kargs):
    """
    This function creates a DBUS service and starts the handler
    """

    # service = kargs.pop('dbus_service')

    # Use glib event loop, on the server side
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    
    # enable multi threading
    gobject.threads_init()

    # Test if daemon is already running
    if isServiceStarted(service):
        peer = Client(service)
        if handler._dbus_kill:
            try:
                peer._dbus_peer.exit()
            except:
                pass

            sys.exit()

        elif handler._dbus_restart:
            pass

        else:
            print "%s daemon already started with pid %s" % (service, peer._dbus_peer.getPid())
            sys.exit(1)

    if handler._dbus_kill:
        sys.exit()

    # We turn our self into a daemon
    _goDaemon()

    print "%s daemon: %s" % (service, os.getpid())

    # Create the service channel and connect the service object to it
    loop = gobject.MainLoop()
    obj  = handler(loop, service, *args, **kargs)

    # enter event loop that handled the RPCs
    loop.run()

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Handlers to the dbus connection
class NoService:
    """
    This class is used when we have no connection with the service
    """
    
    def __init__(self, parent):
        """
        Constructor
        """
        
        self._parent = parent

    def default(self, name, *args, **kargs):
        """
        Updates the status bar in the application with a no-connection notification
        """

        self._parent.showMessage("Service not connected", 1000)
        # print "No connection when using '%s'" % (name) # : %s" % (args)
        return None

    def exit(self, **kargs):
        """
        Ignore exit commands
        """

        pass

    def __getattr__(self, n):
        """
        Remap all function calls to our default method
        """

        return lambda *args, **kargs: self.default(n, args, kargs)

class Remote(object):
    """
    This class handles the interfaces implemented by the remote object
    """
    
    def _bridge(self, f, **kargs):
        """
        Calls the given proxy method with its arguments
        """
        
        return eval("self._dbus_ciface.%s(**kargs)" % (f))

    def __init__(self, iface, ciface):
        """
        Creates a call-bridge for the common remote methods
        """
        self._dbus_iface  = iface
        self._dbus_ciface = ciface
        
        self.exit       = lambda **kargs: self._bridge('exit',       **kargs)
        self.getInfo    = lambda **kargs: self._bridge('getInfo',    **kargs)
        self.getPid     = lambda **kargs: self._bridge('getPid',     **kargs)
        self.getVersion = lambda **kargs: self._bridge('getVersion', **kargs)
        
        # TODO: Why does this not work...
        # for f in ['getVersion', 'getPid', 'getInfo', 'exit']:
        #    self.__setattr__(f, lambda **kargs: self._bridge(f, **kargs))
        
    def __getattr__(self, n):
        """
        Handles the bridging to the supported interface
        """
        
        # print "%s%s%s" % (self._iface.requested_bus_name, 
        #                  self._iface.object_path,
        #                  self._iface.bus_name)

        return getattr(self._dbus_iface, n) 

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Common base class for DBus client/servers
class Base(object):
    """
    Common base class for DBus client/servers
    """

    def __init__(self, service):
        """
        Constructor
        """

        service = service.split('/')
        path    = '/' + '/'.join(service[1:])
        service = service[0]

        self._dbus         = dbus.SessionBus() 
        self._dbus_path    = path
        self._dbus_service = service

    def _showMessage(self, msg, tmo = 0):
        print msg

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# The DBus client class
class Client(Base):
    """
    The base class for a DBus client
    """
    
    def __init__(self, service):
        """
        Constructor
        """

        Base.__init__(self, service)

        if getattr(self, '_debug', False):
            self._dbus_peer = NoService(self)
            return 
        else:
            self._dbus_peer = self._dbus_connect()

        self._dbus.call_on_disconnection(self._dbus_disconnected)

        __decorators__.addActions(self)
        
    def _dbus_add_signal_receiver(self, signal, iface, func):
        """
        This method adds a DBUS signal receiver and ties it to an instance
        function 
        """

        #print "adding signal receiver %s %s %s" % (signal, iface, func)
        self._dbus.add_signal_receiver(func,
                                       # interface_keyword='dbus_interface', 
                                       dbus_interface = iface, 
                                       # member_keyword='member',
                                       # message_keyword='dbus_message',
                                       signal_name = signal)

    def _dbus_is_connected(self):
        """
        Returns the connection state for the DBus
        """

        return self._dbus_peer.__class__ != NoService

    def _dbus_disconnected(self, a):
        """
        Should be called... 
        """
        
        self._dbus_peer = NoService(self)
        self.showMessage("Service connection went away", 2500)

    def _dbus_on_exit(self):
        """
        Ignore...
        """

        pass

    def _dbus_on_exit_error(self, _):
        """
        Ignore...
        """

        pass

    def _dbus_disconnect(self):
        """
        Handles a client request to disconnect from DBus
        """

        self._dbus_peer.exit(reply_handler = self._dbus_on_exit,
                             error_handler = self._dbus_on_exit_error)
        self._dbus_peer = NoService(self)

    def _dbus_connect(self):
        """
        Connects to requested service. Two modes are provided, normal mode terminates if 
        no service is available. The second mode rethrows the exceptionfor later handling.
        The function return handles to the remote object, its interface and its version.
        """
        
        obj   = None
        iface = None
        
        # We first try the get a handled to the remote object 
        try:
            obj = self._dbus.get_object(self._dbus_service, self._dbus_path)

        except Exception, e:
            return NoService(self)

        # ...then we retrieve the two interfaces, 
        # the remote object *must* implement our common interface
        # and then the interface we are interested in
        try:
            ciface = dbus.Interface(obj, dbus_iface)
            xiface = dbus.Interface(obj, self._dbus_service + ".iface")
            
        except Exception, e:
            print str(e)
            sys.exit(1)
        
        #for a in ['dbus_interface', 'requested_bus_name']:
        #    print getattr(xiface, a)

        self._dbus_peer   = obj
        self._dbus_iface  = xiface
        self._dbus_ciface = ciface
    
        # return (obj, iface, ciface, ciface.getVersion())
        remote = Remote(self._dbus_iface, self._dbus_ciface)

        return remote

    @on_dbus_signal_receive('_dbus_service_terminated')
    def _(self, str):
        """
        Call back when service terminates
        """
        
        self._dbus_disconnect()
        self.setServiceState()
        self.showMessage("Service terminated: " % (str), 2500)

    def CommonErrorHandler(self, e):
        """
        Common error handled that is tied to DBus
        """

        print "Server raised an exception: %s" % (str(e))
        print self._dbus, self._dbus_path, self._dbus_service

    def NoReply(self):
        """
        Common reply handled for DBus messages that ignore the reply
        """

        pass

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# The DBus service class
# dbus.server.Server
class Service(dbus.service.Object, Base):
    """
    The DBus base class for services
    """
    
    def __init__(self, loop, service):
        """
        Constructor
        """

        self._loop    = loop
        self._txLock  = threading.RLock()
        self._rxLock  = threading.RLock()
        self._cmdLock = threading.RLock()

        # dbus.server.Server(dbus.SessionBus(), _objs[service], self._dbus)
        Base.__init__(self, service)
        dbus.service.Object.__init__(self, self._dbus, self._dbus_path)
        self._dbus_name = dbus.service.BusName(self._dbus_service, self._dbus)

    @dbus_method(dbus_iface, in_signature='', out_signature='')
    def exit(self):
        """
        A Client request to terminate the service
        """

        print "Daemon exiting"
        self._dbus_service_terminated('User command')
        self._dbus.close()
        # self._loop.quit()

    @dbus_method(dbus_iface, in_signature='', out_signature='i')
    def getVersion(self):
        """
        A Client request for the service version
        """

        return self._version

    @dbus_method(dbus_iface, in_signature='', out_signature='i')
    def getPid(self):
        """
        A Client request for the service process id
        """

        return os.getpid()

    @dbus_method(dbus_iface, in_signature='', out_signature='(ss)')
    def getInfo(self):
        """
        A Client request for version and process id
        """

        return (self._version, os.getpid())

    @on_dbus_signal_send(dbus_iface, signature='s')
    def _dbus_service_terminated(self, reason):
        """
        Method that sends the terminate signal to the client
        """

        pass
