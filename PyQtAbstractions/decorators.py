#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restrictions
# * Modications to this file must be reported to above email

"""
This modules provides a set of decorators that ease the connection of 
UI element actions to methods.
"""

import sys

import inka.__decorators__ as __decorators__
import inka.Qt

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####

__all__ = [
    'ui_class', 
    'on_ui_action', 'on_ui_clicked', 'on_ui_state_changed', 
    'on_ui_changed', 
    'on_ui_finished', 
    'on_ui_value_changed', 
    'on_ui_index_changed',
    'on_ui_text_changed',
    'on_ui_return_pressed',
    'on_ui_short_cut',
    
    'on_signal_receive',
    
    'dbus_method',
    'on_dbus_signal_send',
    'on_dbus_signal_receive',
    
    'locker', 
    ]

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
_dbus_methods   = []
_signal_methods = []
_signal_types   = dict()
_ui_methods     = []
# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Make sure that action method got unique names

def ui_class(cls):
    """
    A decorator that shall be used for a class using ui deocarators
    """

    __decorators__._add_signals(cls)

    global _dbus_methods
    global _signal_methods
    global _ui_methods
    
    # print cls.__name__, _ui_methods, _dbus_methods, _signal_methods
    def make_unique_names(cls, methods, pref):
        n = 0
        new_list = []
        for f in methods:
            name = "_%s_%s_action_%d" % (cls.__name__, pref, n)
            n += 1
        
            # print cls.__name__, f.__name__, name, f
            # print cls.__name__, f.__name__, name, f._on_ui_operation
        
            if not hasattr(cls, f.__name__):
                # print 'skips', f.__name__, name
                continue 

            #if f.__code__ == getattr(cls, f.__name__).__code__:
            #    # print 'skips', f.__name__, name
            #    def skip():
            #        print 'This should never happen'
            #        pass
            #    setattr(cls, '_', skip)
            #    pass # continue

            f.__name__ = name
            setattr(cls, f.__name__, f)
            # print getattr(cls, f.__name__)
            new_list += [f]

        return new_list

    _dbus_methods   = make_unique_names(cls, _dbus_methods,   'dbus')
    _signal_methods = make_unique_names(cls, _signal_methods, 'signal')
    _ui_methods     = make_unique_names(cls, _ui_methods,     'ui')

    if hasattr(cls, '_'):
        # print 'deletes _'
        del cls._

    _signal_methods = __decorators__._create_signal_slots(cls)

    _dbus_methods   = []
    _signal_methods = []
    _ui_methods     = []
    _signal_types   = dict()

    return cls

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Signal decorators

def _on_signal_action_helper(f, obj):
    """
    Interal help method that adds the decoration for the method
    """
    
    if hasattr(f, '_on_signal_operation'):
        l = getattr(f, '_on_signal_operation')
    else:
        global _signal_methods
        _signal_methods += [f]
        l = []

    l += [obj]

    f._on_signal_operation =  l

def _signal_add_decorator(name, type):
    name = 'on_signal_%s' % (name)

    # print '_signal_add_decorator', name
    def method(sig, *args, **kargs):
        def signal_action_helper(f):
            # print '_signal_add_decorator', name, sig, args, kargs
            _on_signal_action_helper(f, (sig, type))
            f._on_signal_args = (args, kargs)
            # f.__pyqtSignature__ = inka.QtCore.pyqtSignature('char*')
            # return inka.QtCore.Slot(*args, **kargs)(f)
            #return f 
        return signal_action_helper
    method.__doc__  = "This method %s decorates signal handler for %s" % (name, type)
    method.__name__ = name
    
    setattr(sys.modules[__name__], method.__name__, method)


for (n, t) in [('receive', 'receive')]:
    _signal_add_decorator(n, t)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# UI decorators

def _ui_on_action_helper(f, obj):
    """
    Interal help method that adds the decoration for the method
    """
    
    if hasattr(f, '_on_ui_operation'):
        l = getattr(f, '_on_ui_operation')
    else:
        global _ui_methods
        _ui_methods += [f]
        l = []

    l += [obj]

    f._on_ui_operation = l

def _ui_add_decorator(name, type):
    name = 'on_ui_%s' % (name)
    def method(*args):
        def ui_action_helper(f):
            for sig in args:
                _ui_on_action_helper(f, (sig, type))
                
            return f
        return ui_action_helper
    method.__doc__  = "This method %s decorates signal handler for %s" % (name, type)
    method.__name__ = name
    
    setattr(sys.modules[__name__], method.__name__, method)

for (n, t) in [('action',           'triggered'), 
               ('clicked',          'clicked'), 
               ('finished',         'editingFinished'), 
               ('state_changed',    'stateChanged'), 
               ('value_changed',    'valueChanged'), 
               ('changed',          'value-changed'),
               ('short_cut',        'short-cut'), 
               ('index_changed',    'currentIndexChanged'), 
               ('text_changed',     'textChanged'), 
               ('return_pressed',   'returnPressed')]:
    _ui_add_decorator(n, t)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# DBus decorators

from dbus.service import signal as on_dbus_signal_send
from dbus.service import method as dbus_method

def _dbus_on_action_helper(f, obj):
    """
    Interal help method that adds the decoration for the method
    """

    if hasattr(f, '_on_dbus_operation'):
        l = getattr(f, '_on_dbus_operation')
    else:
        global _dbus_methods
        _dbus_methods += [f]
        l = []

    l += [obj]

    f._on_dbus_operation = l

def _dbus_add_decorator(name, type):
    name = 'on_dbus_%s' % (name)
    def method(*args):
        def dbus_action_helper(f):
            for sig in args:
                _dbus_on_action_helper(f, (sig, type))
                
            return f
        return dbus_action_helper
    method.__doc__  = "This method %s decorates signal handler for %s" % (name, type)
    method.__name__ = name
    
    setattr(sys.modules[__name__], method.__name__, method)

for (n, t) in [('signal_receive', 'signal')]:
    _dbus_add_decorator(n, t)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Thread decorators

def locker(*lock):
    """
    decorator:
    This is a decoration method that acquires the locks in the parameter list
    Then invokes the method and finaly releases the locks
    """

    def wrapper(func):
        """ 
        This function wraps the actual function call insides the acquired locks
        """

        def caller(self, *args, **kargs):
            """
            This function acquires the locks and calls the method
            """

            # Acquire the locks
            for l in lock:
                # print "Acquire lock: %s %s" % (func, l)
                eval('self._%s.acquire()' % (l))

            # calls the function
            try:
                res = func(self, *args, **kargs)
            finally:
                # allways make sure that all locks are released
                for l in lock:
                    # print "Release lock: %s %s" % (func, l)
                    eval('self._%s.release()' % (l))

            return res
        return caller
    return wrapper

