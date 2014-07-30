#!/usr/bin/python

import argparse
import math

parser = argparse.ArgumentParser(
        description = 'Generate detailed spirals for buffer testing')

parser.add_argument('-r', '--radius', type = float, required = True,
        dest = 'r_outer',
        help = 'Outer radius of spiral or circle to generate')
parser.add_argument('-n', type = int, required = True,
        dest = 'count',
        help = 'Number of moves to produce. The number of '
        'cycles generated depends on this, the distance per move, '
        'and the radius')
parser.add_argument('-d', '--distance', type = float, default = float(1.0),
        dest = 'dist',
        help = 'Distance in mm each move should cover, '
        'defaults to %(default)s')
parser.add_argument('-s', '--speed', type = float, default = float(90.0),
        dest = 'speed',
        help = 'Speed at which to print. Defaults to %(default)s')
parser.add_argument('-e', '--extrusion', type = float, default = float(0.0),
        dest = 'extrusion',
        help = 'mm feedstock per mm gantry movement. '
        'Omit to disable extrusion. Formula is cross sectional area of '
        'extrusion divided by cross sectional area of feedstock. '
        'With 1.75 mm feedstock and 0.2 layers, this value is about 0.0333')
parser.add_argument('-R', '--radius-inner', type = float, default = None,
        dest = 'r_inner',
        help = 'Inner radius of spiral to generate. '
        'Omit to generate a circle')
parser.add_argument('--radius-transition', type = int, default = None,
        dest = 'r_count',
        help = 'Number of moves it takes to go from outer radius to '
        'inner radius. Only useful with --radius-inner. Set to less than -n '
        ' to have the spiral radius oscillate between outer and '
        'inner radius')
args = parser.parse_args()

if None is args.r_count:
    args.r_count = args.count
if None is args.r_inner:
    args.r_inner = args.r_outer

r_mult = math.pi / args.r_count
r_delta = args.r_inner - args.r_outer
feedstock_per_mm = args.extrusion
speed = args.speed

def get_radius(i):
    m = 0.5 - 0.5 * math.cos(i * r_mult)
    return args.r_outer + r_delta * m

def get_xy_coords(radii):
    a = 0.0
    for r in radii:
        da = args.dist / r
        a += da
        a = math.fmod(a, 2 * math.pi)
        yield (r * math.cos(a), r * math.sin(a))

def get_xya(xys):
    last_xy = None
    last_a = 0.0
    for xy in xys:
        if None is not last_xy:
            last_a += feedstock_per_mm * math.hypot(
                    *(a - b for (a, b) in zip(last_xy, xy)))
        last_xy = xy
        yield tuple(list(xy) + [last_a])

def get_command(x, y, a, f):
    ret = "{\"command\":{\"function\":\"move\","\
    "\"parameters\":{"\
        "\"x\":%s,"\
        "\"y\":%s,"\
        "\"z\":0,"\
        "\"a\":%s,"\
        "\"feedrate\":%s"\
    "},\"tags\":[\"Move\"],"\
    "\"metadata\":{"\
        "\"relative\":{"\
            "\"x\":false,"\
            "\"y\":false,"\
            "\"z\":true,"\
            "\"a\":false"\
        "}"\
    "}}}"
    return ret % (x, y, a, f)
        

radii = (get_radius(i) for i in xrange(args.count))
xys = get_xy_coords(radii)
xyas = get_xya(xys)
commands = (get_command(*(list(xya) + [speed])) for xya in xyas)

first_command = True
for command in commands:
    if first_command:
        print '[' + command
        first_command = False
    else:
        print ',' + command
print ']'

