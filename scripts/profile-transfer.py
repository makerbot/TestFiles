#!/usr/bin/python

import argparse
import json
import sys

parser = argparse.ArgumentParser(
        description = 'Compare two custom profiles and apply the '
        'difference to a third')

parser.add_argument('CLEAN', type = str,
        help = 'Path to the unmodified profile')
parser.add_argument('DIRTY', type = str,
        help = 'Path to the profile with your changes')
parser.add_argument('BASE', type = str,
        help = 'Path to the profile on top of which  to apply the changes')
parser.add_argument('OUT', type = str,
        help = 'Path where to write generated profile')

args = parser.parse_args()

with open(args.CLEAN, 'r') as ifile:
    clean_dict = json.load(ifile)
with open(args.DIRTY, 'r') as ifile:
    dirty_dict = json.load(ifile)
with open(args.BASE, 'r') as ifile:
    base_dict = json.load(ifile)

def primitive(k):
    return type(k) not in (list, dict)

def diff(a, b, c):
    if not (type(a) == type(b) and type(b) == type(c)):
        raise ValueError('type mismatch')
    if isinstance(a, dict):
        for k in b:
            if k not in a or k not in c:
                c[k] = b[k]
            elif primitive(b[k]):
                if b[k] != a[k]:
                    c[k] = b[k]
            else:
                diff(a[k], b[k], c[k])
    elif isinstance(a, list):
        if not (len(a) == len(b) and len(b) == len(c)):
            raise ValueError('length mismatch')
        for i in xrange(len(b)):
            if not primitive(b[i]):
                diff(a[i], b[i], c[i])
            elif b[i] != a[i]:
                c[i] = b[i]
    else:
        raise ValueError('python reference semantics prohibit this')

diff(clean_dict, dirty_dict, base_dict)

if args.OUT == '-':
    json.dump(base_dict, sys.stdout, indent = 4, sort_keys = True)
else:
    with open(args.OUT, 'w') as ofile:
        json.dump(base_dict, ofile, indent = 4, sort_keys = True)