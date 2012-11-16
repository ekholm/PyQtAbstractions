#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

class Handler(object):
    def __init__(self, owner):
        self._owner = owner
        self._sm    = None

    def set(self, sm, *args, **kargs):
        if not sm:
            self._sm = None
            return True

        if self._sm:
            return False

        self._sm = sm(self, self._owner)
        self._sm.init(*args, **kargs)

        return self._sm.start()

    def __getattr__(self, attr):
        if self._sm:
            return getattr(self._sm, attr)
        else:
            return lambda *args, **kargs : None

class Base(object):
    _debug = False

    # <state> : (<action>, <action method>,    <new state>)
    # <state> : (<action>, <action method>,    <new state method>)
    # <state> : (<action>, [<action method>+], <new state>)
    # <state> : (<action>, [<action method>+], <new state method>)

    def __init__(self, handler, owner):
        self._handler = handler
        self.owner    = owner
        self.current  = 'start'

    def start(self):
        if self.current != 'start':
            return False

        self.action(None) 
        return True
        
    def action(self, event, *args):
        if self._debug:
            print """SM: event "%s" in state "%s" """ % (event, self.current)

        # if action is None, then it's the default action
        #if action not in self.matrix and action != None:
        #    print "Invalid action: %s" % (action)
        #    return

        doneAction = False

        actions = self.matrix[self.current]
        if isinstance(actions, tuple):
            actions = [actions]

        # Traverse all action entries for state
        for (e, fl, n) in actions:
            # if correct action entry, do the action
            if e == event:
                doneAction = True

                # the list of functions might be a single item, 
                # make it a list then
                if not isinstance(fl, list):
                    fl = [fl]

                # now traverse the list and do all actions
                for f in fl:
                    if f != None:
                        if self._debug:
                            print """SM: action "%s" in state "%s" """ % (f.__name__, self.current)
                        doneAction = True
                        if args != ():
                            f(args)
                        else:
                            f()

                # now we check if we need to change state, 
                # if new state is a method, call it to get new state
                if callable(n):
                    n = n()

                # if new state is not None, we are done with current action
                # and change state
                if n != None:
                    self._newState(n)
                    return

        # Here we check that we really has done any action for the state
        # if not there is some error... or it completely normal
        if not doneAction and event != None:
            print """Untreated event "%s" in state "%s" """ % (event, self.current)

    def getState(self):
        return self.current

    def _newState(self, state):
        if self._debug:
            print """SM: trans "%s" -> "%s" """ % (self.current, state)

        if state == 'done':
            self._handler.set(None)
            return 

        if state not in self.matrix:
            print """Invalid state: "%s" """ % (state)
            return

        self.current = state
        self.action(None)
