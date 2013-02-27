#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

"""
A modules that provides abstractions for parameter handling
"""

import argparse

def add(name, **kwargs):
    return (name, kwargs)

class Parser:
    class C(object):
        pass

    def __init__(self, *args, **kwargs):
        parser = argparse.ArgumentParser(*kwargs)
        for c in args:
            for (n, p) in c._params:
                parser.add_argument(n, **p)
        parser.parse_args(namespace = Parser.C)

        for c in args:
            for (n, p) in c._params:
                a = p['dest']
                setattr(c, a, getattr(Parser.C, a))
