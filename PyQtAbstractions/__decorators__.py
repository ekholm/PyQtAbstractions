#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restrictions
# * Modications to this file must be reported to above email

import inspect
import re
import sys
import types

# import PyQtAbstractions.decorators as decorators
import decorators

from __qt_modules__ import *
    
# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Methods for adding the signal call backs

def isActionAdded(self, name, elem, action, func):
    """
    self   - Widget
    name   - class of action types
    elem   - UI element
    action - action type
    func   - call back function
    """

    op_attr = '_{:s}_actions_added'.format(name)
    # print('isActionAdded:', self.__class__.__name__, name, elem, action, func)

    # print(self, op_attr)
    if not hasattr(self, op_attr):
        setattr(self, op_attr, {})
    op_attr = getattr(self, op_attr)

    key = (elem, action, func)

    if key in op_attr:
        # print('Already added', key)
        return True

    op_attr[key] = True

    return False

def _addOperations(self, name):
    # mo      = self.metaObject()
    op_name = '_on_{:s}_operation'.format(name)
    
    for elem in dir(self):
        if not hasattr(self, elem):
            continue 
        func = getattr(self, elem)
        if not inspect.ismethod(func):
            continue
        # print('addOperations:', func.im_class, func.im_self, func.im_func)
        # Add method hooks for the UI 
        if not hasattr(func, op_name):
            continue
        # Iterate over all objects to listen to
        for action in getattr(func, op_name):
            if action[0] == 'pre':
                # print(action)
                (_, op_func, params) = action
                op_func(self, name, elem, params, func)
            else:
                (elem, action) = action
                # print('addOperaions:', name, elem, action, func)
                op_func = eval('_{:s}_add_action_helper'.format(name))
                op_func(self, name, elem, action, func)

def addActions(self):
    """
    Help method that adds all the connection for a class
    """
    
    if hasattr(self, '_ui'):
        addActions(self._ui)

    for name in ['dbus', 'signal', 'ui']:
        _addOperations(self, name)

# run decorators that need to be executed prior to instatiation
def addPreActions(cls):
    """
    Help method that adds all the connection for a class
    """

    if hasattr(cls, '_ui'):
        addActions(cls._ui)

    for name in ['dbus', 'signal', 'ui']:
        _addOperations(cls, '{:s}_pre'.format(name))

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Signal/Slots
#
#   state_change = Signal(int, str)
#
#    @on_signal_receive('state_change')
#    def _(self, a, b):
#        print("Slot1", 2 * a, b)
#
#    @on_signal_receive('state_change')
#    def _(self, a, b):
#        print("Slot2", 2 * a, b)
#
#    def state_change_example(self):
#        print(type(self.state_change))
#        # print(type(self.state_change_type))
#        print(self.state_change.emit(42, 'test'))
#        state_change = QtCore.Signal(int, str)
#        return

def _add_signals(cls):
    for elem in dir(cls):
        sig = getattr(cls, elem)
        if isinstance(sig, QtCore.Signal):
            if sig in decorators._signal_types:
                #print(dir(sig))
                #print(sig.__str__())
                #sys.exit()
                
                # sig._signal_name = elem
                # print('_add_signals', elem, sig)
                decorators._signal_types[elem] = decorators._signal_types[sig]
                del decorators._signal_types[sig]

def _create_signal_slot(self, f):
    for (n, t) in f._on_signal_operation:
        (args, kargs) = f._signal_types[n]
        if not Qt.isPyQt4:
            f = QtCore.Slot(*args, **kargs)(f)
            setattr(self, f.__name__, f)
        return getattr(self, f.__name__)

def _create_signal_slots(cls):
    new_list = []
    for f in decorators._signal_methods:
        # print('_create_signal_slot', f.__name__, f.__code__)
        for (n, t) in f._on_signal_operation:
            (args, kargs) = decorators._signal_types[n]
            if not hasattr(f, '_signal_types'):
                f._signal_types = dict()
            f._signal_types[n] = (args, kargs)
            #if Qt.isPyQt4:
            #    f = QtCore.Slot(*args, **kargs)(f)
            #    setattr(cls, f.__name__, f)

            # print('func', args)
            # print(f.func_dict)
            # setattr(cls, f.__name__, f)
            # print(getattr(cls, f.__name__))

        new_list += [f]

    return new_list

def _signal_add_action(self, elem, action, func):
    """
    self   - Widget
    elem   - Signal name
    action - trigger on action ('receive')
    func   - call back function
    """

    if not hasattr(self, elem) and not (action == 'short-cut'):
        print('Signal not declared: {:s} {:s}'.format(elem, action))
        return
    
    actions = [action]
    
    # print('_signal_add_action:', self.__class__.__name__, elem, action, actions, func.__name__)
    for a in actions:
        try:
            if not isActionAdded(self, 'signal', elem, a, func.__name__):
                #print('_signal_add_action:', self.__class__.__name__, elem, a, func.__name__, func, self)
                #print(getattr(self, func.__name__))
                signal = getattr(self, elem)
                signal.connect(func)
        except:
            pass

def _signal_add_action_helper(self, name, elem, action, func):
    """
    name   - type of operation 'signal'
    elem   - Signal name
    action - trigger on action ('receive')
    func   - call back function
    """

    # print('_signal_add_action_helper', self, name, elem, action, func.__name__)
    func = _create_signal_slot(self, func)

    obj = self    # This is a QObject subclass
        
    # If object is is a regular expression
    if type(elem) is re._pattern_type:
        for o in dir(obj):
            if elem.match(o):
                # print 'pattern', self, obj, o, elem, action, func
                _signal_add_action(obj, o, action, func)
    else:
        # print('_signal_add_action_helper', self, elem, action, func)
        _signal_add_action(obj, elem, action, func)
                         
# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# UI decorators

def _ui_add_action(self, elem, action, func):
    """
    self   - Widget
    elem   - UI element
    action - trigger on action
    func   - call back function
    """

    if not hasattr(self, elem) and not (action == 'short-cut'):
        # print('Unknown attribute:', self, elem, action, func)
        return
    
    if action == 'value-changed':
        actions = ['editingFinished', 'valueChanged', 'currentIndexChanged', 'textChanged', 'stateChanged']
    else:
        actions = [action]
    
    # print('_ui_add_action:', self.__class__.__name__, elem, action, actions, func.__name__)
    for a in actions:
        try:
            if not isActionAdded(self, 'ui', elem, a, func.__name__):
                if a == 'short-cut':
                    action = QtGui.QAction(self)
                    action.setShortcut(QtGui.QKeySequence(elem))
                    action.triggered.connect(func)
                    self.addAction(action)
                else:
                    #print('_ui_add_action connecting:', self.__class__.__name__, elem, a, func.__name__)
                    #print('    ', getattr(self, elem))
                    ui = getattr(getattr(self, elem), a)
                    #print('    ', ui)
                    ui.connect(func)
        except:
            pass

def _ui_add_action_helper(self, name, elem, action, func):
    """
    name   - type of operation 'ui'
    elem   - UI element
    action - trigger on action
    func   - call back function
    """

    # print('_ui_add_action_helper', self, name, elem, action, func.__name__)

    # handle either the application class or a widget directly
    # TODO: for short-cuts this does not work properly
    if name == 'ui' and hasattr(self, '_ui'):
        obj = self._ui # Non widget subclass shall have .ui member
    else:
        obj = self    # This is a widget subclass
        
    # If object is is a regular expression
    if type(elem) is re._pattern_type:
        for o in dir(obj):
            if elem.match(o):
                # print('pattern', self, obj, o, elem, action, func)
                _ui_add_action(obj, o, action, func)
    else:
        # print('_ui_add_action_helper', self, name, elem, action, func)
        _ui_add_action(obj, elem, action, func)
                         
# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# DBus decorators
def _dbus_add_action_helper(self, name, elem, action, func):
    """
    name   - type of operation 'dbus'
    elem   - element (DBUS signal name)
    action - trigger on action  ('signal')
    func   - call back
    """
    
    # print('_dbus_add_action_helper', name, elem, action, func.__name__)

    if hasattr(self, '_dbus_service'):
        # print(name, elem, action, func)
        dbus_iface = self._dbus_service + ".iface"
        if not isActionAdded(self, 'dbus', elem, dbus_iface + "." + action, func.__name__):
            self._dbus_add_signal_receiver(elem, dbus_iface, func)
