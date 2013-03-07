#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

"""
A modules that provides abstractions for parameter handling
"""

import argparse
import copy

def add(name, **kwargs):
    return [name, kwargs]

class Parser:
    class C(object):
        pass

    def __init__(self, *args, **kwargs):
        try:
            global_params = kwargs.get('global_params', None)
            del kwargs['global_params']
        except:
            pass

        # create the normal parser
        parser = argparse.ArgumentParser(**kwargs)

        pre = ''     # the prefix for the variable
        gp  = parser # default parser is top lever parser

        # first, handle the global parametrs
        for pp in global_params:
            
            # check if we have special entry in list
            if type(pp) == tuple:
                # This entry is for sub parser heading (name and command line prefix)
                (name, pre) = pp
                gp = parser.add_argument_group(name)
                continue
            elif type(pp) == str:
                # This entry is for sub parser heading (name but no command line prefix)
                gp = parser.add_argument_group(pp)
                continue
                
            # if we end up here, we have a command line argument specification
            (n, p) = pp

            # add a leading underscore if missing
            p = dict(p)
            if p['dest'][0] != '_':
                p['dest'] = "_{:s}".format(p['dest'])

            # create the command line argument name
            if pre != "": 
                p['dest'] = '_{:s}{:s}'.format(pre, p['dest'])
                n = '--{:s}-{:s}'.format(pre, n)
            else:
                n = '--{:s}'.format(n)

            gp.add_argument(n, **p)
            
        # add arguments from all clients
        for c in args:
            # first, check if supplied client has private arguments
            if not hasattr(c, '_params'):
                continue

            # create the subparser for the client
            grp = parser.add_argument_group(c.__name__)

            # and add is argments
            for (n, p) in c._params:
                # modify the local storage name for the value
                p = dict(p)
                if p['dest'][0] != '_':
                    p['dest'] = "_{:s}".format(p['dest'])

                p['dest'] = '_{:s}{:s}'.format(c.__name__, p['dest'])

                # create the name for the 
                if hasattr(c, '_params_pre'):
                    n = '--{:s}-{:s}'.format(c._params_pre, n)
                else:
                    n = '--{:s}'.format(n)

                grp.add_argument(n, **p)

        # parser the argv
        parser.parse_args(namespace = Parser.C)

        # now store the values within each client
        pre = ''

        # start with the global arguments
        for pp in global_params:
            # handle the meta information
            if type(pp) == tuple:
                (name, pre) = pp
                continue
            elif type(pp) == str:
                continue

            (_, p) = pp

            # add a leading underscore if missing
            p = dict(p)
            if p['dest'][0] != '_':
                p['dest'] = "_{:s}".format(p['dest'])
            elif pre != "":
                print 'bas'

            if pre != '':
                dest = '_{:s}{:s}'.format(pre, p['dest'])
            else:
                dest = '{:s}'.format(p['dest'])
            
            # store the value in the destination client
            for c in args:
                setattr(c, dest, getattr(Parser.C, dest))
                
        for c in args:
            if not hasattr(c, '_params'):
                continue

            for (n, p) in c._params:
                # add a leading underscore if missing
                p = dict(p)
                if p['dest'][0] != '_':
                    p['dest'] = "_{:s}".format(p['dest'])

                # store the value in the destination client
                src = '_{:s}{:s}'.format(c.__name__, p['dest'])
                setattr(c , p['dest'], getattr(Parser.C, src))
