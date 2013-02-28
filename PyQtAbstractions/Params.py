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
    return (name, kwargs)

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

        # add global arguments
        for (n, p) in global_params:
            n = '--%s' % (n)
            parser.add_argument(n, **p)
            
        # add arguments from all clients
        for c in args:
            grp = parser.add_argument_group(c.__name__)
            for (n, p) in c._params:
                p = copy.deepcopy(p)
                p['dest'] = '_%s_%s' % (c.__name__, p['dest'])
                if hasattr(c, '_params_pre'):
                    n = '--%s-%s' % (c._params_pre, n)
                else:
                    n = '--%s' % (n)
                grp.add_argument(n, **p)

        # parser the argv
        parser.parse_args(namespace = Parser.C)

        # now store the values within each client
        for (n, p) in global_params:
            dest = p['dest']
            for c in args:
                setattr(c, dest, getattr(Parser.C, dest))
                
        for c in args:
            for (n, p) in c._params:
                src = '_%s_%s' % (c.__name__, p['dest'])
                setattr(c , p['dest'], getattr(Parser.C, src))
