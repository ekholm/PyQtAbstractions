#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

# TODO: PyQtAbstractions

import QSource

import PyQt4
from PyQtAbstractions import *

import dbus
import dbus.mainloop.glib
import dbus.service
import re

# import pymca_resource

SOURCE_TYPE = 'DBUS'
dbus_obj   = "se.esrf.pymca"
dbus_iface = dbus_obj + ".iface" 

def createButton(self):
    # setattr(self, 'openDBus', openDBus)
    self.dbusIcon = QtGui.QIcon(QtGui.QPixmap(":/icons/connected.png"))

    self.dbusButton = QtGui.QToolButton(self.fileWidget)
    self.dbusButton.setIcon(self.dbusIcon)
    self.dbusButton.setToolTip("Open new DBUS source")
    self.dbusButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum))
    self.dbusButton.clicked.connect(self.openDBus)

    return self.dbusButton

def openDBus(self):
    # self.dbus = DBus(self)

    services = findServices(r'.*pymca')

    if not len(services):
        pressed =  QtGui.QMessageBox.information(self,
                                                 "No DBus services",
                                                 "No DBus services found for PyMCA", 
                                                 "Ok")

        if pressed == 0:
            return

    menu = QtGui.QMenu()
    for service in services:
        desc  = getDBusDesc(service)
        sname = 'dbus:' + service
        if desc:
            action =  menu.addAction(desc + ' - ' + sname,
                                     lambda i = sname : self.openFile(i, dbus_session = True))
            action.setIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/analysis.png")))

    menu.exec_(self.cursor().pos())

def findServices(service):
    pattern = re.compile(service)
    bus     = dbus.SessionBus() 

    services = []
    for a in bus.list_names():

        if pattern.match(a):
            services += [a]

    return services

class NoService:
    def __init__(self, parent):
        pass

def getDBusDesc(service):
    service = service.split(':')[-1]
    bus   = dbus.SessionBus() 
    obj   = bus.get_object(service, "/")
    iface = dbus.Interface(obj, service + ".iface")
    desc = iface.get_info()

    return desc


class DBus:
    def __init__(self, parent):
        self._parent = parent

        self._dbus         = dbus.SessionBus() 
        self._dbus_service = "se.PyQtAbstractions.pymca"
        self._dbus_peer    = self._dbus_connect()
        self._dbus.call_on_disconnection(self._dbus_disconnected)

        self._dbus_add_signal_receiver(self, 'new_spectrum_data', self._dbus_service, self.NewDBusData)
        
    def _dbus_add_signal_receiver(self, signal, iface, func):
        """
        This method adds a DBUS signal receiver and ties it to an instance
        function 
        """

        # print("adding signal receiver {:s} {:s}".format(signal, getattr(self, signal)))
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
            obj = self._dbus.get_object(self._dbus_service, "/")

        except Exception, e:
            return NoService(self)

        # ...then we retrieve the two interfaces, 
        # the remote object *must* implement our common interface
        # and then the interface we are interested in
        try:
            ciface = dbus.Interface(obj, IFACE)
            xiface = dbus.Interface(obj, self._dbus_service + ".iface")
            
        except Exception, e:
            print(str(e))
            sys.exit(1)
        
        #for a in ['dbus_interface', 'requested_bus_name']:
        #    print(getattr(xiface, a))

        self._dbus_peer   = obj
        self._dbus_iface  = xiface
        self._dbus_ciface = ciface
    
        # return (obj, iface, ciface, ciface.getVersion())
        remote = Remote(self._dbus_iface, self._dbus_ciface)

        return remote


class DBusWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.source = None
        self.data = None

    def on_refresh(self):
        print('refresh pressed', self.source)

        if self.source == None:
            QtGui.QMessageBox.information(self,
                                          "No DBus services",
                                          "No DBus services connected PyMCA", 
                                          "Ok")
            return

    def setDataSource(self, source):
        print('DBusWidget::setDatSource called', source)
        self.source = source

        self.on_refresh()
        

def Widget():
    widget = Qt.load_ui(':/forms/pyMcaDBus.ui')
    widget.refresh.clicked.connect(widget.on_refresh)

    # self._ui.setParent(self)

    return widget

class DataSource(QSource.QSource):
    def __init__(self, service):
        QSource.QSource.__init__(self)

        print('DataSource DBUS: ', service)
        self.service = service.split(':')[-1]

        # Reqired by PyMca?
        self.sourceName   = getDBusDesc(self.service)
        self.sourceType   = SOURCE_TYPE

        # def getDataObject(self, key_list, selection = None, poll = True):
