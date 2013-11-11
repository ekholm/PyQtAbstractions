#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

import inspect
import sys
import traceback

class Handler(object):
    def __init__(self, owner):
        self._owner = owner
        self._sm    = None

    def set(self, sm, *args, **kwargs):
        if not sm:
            self._sm = None
            if hasattr(self._owner, 'stateMachineDone'):
                self._owner.stateMachineDone()
            return True

        if self._sm:
            return False

        self._sm = sm(self, self._owner)
        self._sm.init(*args, **kwargs)
        self._sm._configure_sm()

        return self._sm.start()

    def __getattr__(self, attr):
        if self._sm:
            return getattr(self._sm, attr)
        else:
            return lambda *args, **kwargs : None

class Base(object):
    _debug = True

    # <state> : (<action>, <action method>,    <new state>)
    # <state> : (<action>, <action method>,    <new state method>)
    # <state> : (<action>, [<action method>+], <new state>)
    # <state> : (<action>, [<action method>+], <new state method>)

    def __init__(self, handler, owner):
        self._handler       = handler
        self.owner          = owner
        self.current        = 'start'
        self.in_action      = False
        self.pending_action = None

    def init(self):
        pass

    def _configure_sm(self):
        self.sm_matrix = {}
        # print self.__class__.__name__
        self._add_sm(self.matrix)
        # self._print()

    def _print(self):
        for (k, v) in sorted(self.sm_matrix.items()):
            if type(v) == list:
                print('"{}":'.format(k))
                for a in v:
                    print('    {}'.format(a))
            else:
                print('"{}": {}'.format(k, v))

    def _update_tuple(self, item, translate):
        if len(item) == 0:
            return item

        (a, f, e) = item

        if type(e) != str:
            return item

        if e not in translate:
            return item

        return (a, f, translate[e])

    def _update_tuples(self, data, translate):
        if type(data) == list:
            new_data = []
            for d in data:
                new_data += [self._update_tuple(d, translate)]
            return new_data
        else:
            return self._update_tuple(data, translate)
                
    def _add_sm(self, sm, rename = {}, translate = {}):
        if type(sm) == dict:
            # do update of key names
            tmp = {}
            for (k, v) in sm.items():
                # if a state name is translated, we remove its actions
                if k in translate:
                    continue

                # check if a "new state name" need to be updated
                v = self._update_tuples(v, translate)

                # check if state name need to be updated
                if k in rename:
                    k = rename[k]
                    
                    # None means, remove action
                    if k == None:
                        continue

                # check for duplicates
                if k in self.sm_matrix:
                    print("Duplicate state name: {:s}".format(k))
                    sys.exit(1)
                    
                tmp[k] = v

            self.sm_matrix = dict(self.sm_matrix.items() + tmp.items())

        elif type(sm) == list:
            for s in sm:
                self._add_sm(s)

        elif type(sm) == tuple:
            self._add_sm(*sm)

        else:
            print("Illegal matrix defined! {}".format(type(sm)))
            traceback.print_stack()
            sys.exit(1)
 
    def init(self, *args, **kwargs):
        pass

    def start(self):
        if self.current != 'start':
            return False

        self.action(None) 
        return True
        
    def action(self, event, *args):
        if self.in_action:
            self.pending_action = (event, args)
            return

        self.in_action = True
        self._action(event, *args)
        self.in_action = False

        if self.pending_action:
            (event, args) = self.pending_action
            self.pending_action = None
            self.action(event, *args)

    def _action(self, event, *args):
        if self._debug:
            print("""SM: event "{:s}" in state "{:s}" """.format(event, self.current))

        # if action is None, then it's the default action
        #if action not in self.sm_matrix and action != None:
        #    print("Invalid action: {:s}".format(action))
        #    return

        doneAction = False

        actions = self.sm_matrix[self.current]
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
                            print("""SM: action "{:s}" in state "{:s}" """.format(f.__name__, self.current))
                        doneAction = True
                        if args != ():
                            if hasattr(f, 'im_self') and f.im_self:
                                f(args)
                            else:
                                f(self, args)
                        else:
                            if hasattr(f, 'im_self') and f.im_self:
                                f()
                            else:
                                f(self)

                # now we check if we need to change state, 
                # if new state is a method, call it to get new state
                if callable(n):
                    if hasattr(f, 'im_self') and f.im_self:
                        n = n()
                    else:
                        n = n(self)

                # if new state is not None, we are done with current action
                # and change state
                if n != None:
                    self._newState(n)
                    return

        # Here we check that we really has done any action for the state
        # if not there is some error... or it completely normal
        if not doneAction and event != None:
            print("""Untreated event "{:s}" in state "{:s}" """.format(event, self.current))
            self._handler.set(None)

    def getState(self):
        return self.current

    def _newState(self, state):
        if self._debug:
            print("""SM: trans "{:s}" -> "{:s}" """.format(self.current, state))

        if state == 'done':
            self._handler.set(None)
            return 

        if state not in self.sm_matrix:
            print("""Invalid state: "{:s}" """.format(state))
            self._handler.set(None)
            return

        self.current = state
        self.action(None)
