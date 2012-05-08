#!/usr/bin/python

import os
import sys
import re
from pysvg.structure import svg
from pysvg.shape import line
from pysvg.builders import StyleBuilder
from math import sqrt

layer_begin = re.compile('^\((<layer>|Slice) [\d.]+.*\)$')
gcode_move = re.compile('G1 (([XYZEF])(-?\d+\.?\d*))? (([XYZEF])(-?\d+\.?\d*))? (([XYZEF])(-?\d+\.?\d*))? (([XYZEF])(-?\d+\.?\d*))? (([XYZEF])(-?\d+\.?\d*))?')
gcode_axis = re.compile('(([XYZEF])(-?\d+\.?\d*))')
gcode_command_code = re.compile('([A-Z]\d+)(\s|$)')

gcode_file = sys.argv[1]
dump_dir = sys.argv[2]
factor = int(sys.argv[3])
extruder_mode = int(sys.argv[4])

min_x = 0
min_y = 0

def layer_filename(layer_num):
    return dump_dir+'/layer_'+str(layer_num)+'.svg'

class GCode(object):
    (MOVE, EXTRUDE) = range(2)
    
    @staticmethod
    def code_from_line(gcode_line):
        match = gcode_command_code.match(gcode_line)

        if match is None: return None
        else: return match.group(1)
        
    @staticmethod
    def line_type(gcode_line):
        code = GCode.code_from_line(gcode_line)

        if code == "G1":
            return GCode.MOVE
        if code in ("M101", "M102", "M103", "M108"):
            return GCode.EXTRUDE

    @staticmethod
    def parse_G1_line(gcode_line):
        match = gcode_move.match(gcode_line)
    
        if match is None:
            return None

        parsed = dict()
        for match in gcode_axis.findall(gcode_line):
            parsed[match.group(2)] = match.group(3)

        return parsed


class Coord(object):
    def __init__(self, x=0, y=0, z=0):
        self.x = x - min_x
        self.y = y - min_y 
        self.z = z

    def copy(self, other):
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y, self.z - other.z)

class Movement(Coord):
    def __init__(self, start, end, speed):
        self.start = Coord()
        self.start.copy(start)

        self.end = Coord()
        self.end.copy(end)

        self.speed = speed

        self.copy(end - start)

    def toSVG(self, style):
        myline = line(self.start.x * factor, self.start.y * factor,
                      self.end.x * factor, self.end.y * factor)
        myline.set_style(style.getStyle())
        return myline

    def layer_change(self):
        return self.z > 0

    def distance(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def duration(self):
        return self.distance() / (self.speed / 60)

class Position(Coord):
    def move(self, newpos, speed):
        movement = Movement(self, newpos, speed)

        myz = movement.z
        self.copy(newpos)
        return movement

    def gcode_move(self, gcode):
        values = GCode.parse_G1_line(gcode)

        if values is None: return None

        return self.move(Coord(values['X'], values['Y'], values['G']),
                         values['F'])

class Extruder(object):
    extrude_style = StyleBuilder()
    extrude_style.setStrokeWidth(.3 * factor)
    extrude_style.setStroke('red')

    move_style = StyleBuilder()
    move_style.setStrokeWidth(.3 * factor)
    move_style.setStroke('blue')

    def __init__(self, stats):
        self.extruding = False
        self.stats = stats

    def is_extruding(self):
        return self.extruding

    def set_extruding(self, val):
        if self.extruding != val:
            stats.switch_extruder()
            self.extruding = val

    def from_gcode(self, gcode_line):
        code = GCode.code_from_line(gcode_line)
        if code in ("M102", "M103"):
            self.set_extruding(False)
        elif code == "M101":
            self.set_extruding(True)

    def getStyle(self):
        if self.extruding:
            return self.extrude_style
        else:
            return self.move_style

class StatsCollector(object):
    def __init__(self, layernum):
        self.new_layer(layernum)
        
    def add_move(self, move):
        self.move_times.append(move.duration())

    def add_extrude(self, move):
        self.extrude_times.append(move.duration())

    def switch_extruder(self):
        self.extruder_switches += 1

    def stats_filename(self):
        return dump_dir + "/layer_" + str(self.layernum) + "_stats.txt"

    def move_time(self):
        return sum(self.move_times)

    def extrude_time(self):
        return sum(self.extrude_times)

    def total_time(self):
        return self.move_time() + self.extrude_time()

    def write(self):
        fh = open(self.stats_filename(), "w")
        fh.write("Move time: " + str(self.move_time()) + "\n")
        fh.write("Number of moves: " + str(len(self.move_times)) + "\n")
        fh.write("Extrude time: " + str(self.extrude_time()) + "\n")
        fh.write("Number of extrudes: " + str(len(self.extrude_times)) + "\n")
        fh.write("Total time: " + str(self.total_time()) + "\n")
        fh.write("Extruder switches: " + str(self.extruder_switches))
        fh.close()

    def new_layer(self, layernum):
        self.move_times = []
        self.extrude_times = []
        self.layernum = layernum
        self.extruder_switches = 0

################################################################################

gcode_fh = open(gcode_file, "r")

#find the bounds of the object
for gcode_line in gcode_fh.readlines():
    gcode_line = gcode_line.rstrip()
    values = GCode.parse_G1_line(gcode_line)

    if values is None: continue

    if values['X'] < min_x: min_x = values['X']
    if values['Y'] < min_y: min_y = values['Y']

print "min_x: " + str(min_x)
print "min_y: " + str(min_y)

gcode_fh.close()
gcode_fh = open(gcode_file, "r")

cur = Position()
out = None
layer_num = None

stats = StatsCollector(0)
extruder = Extruder(stats)

for gcode_line in gcode_fh.readlines():
    gcode_line = gcode_line.rstrip()

    command = GCode.line_type(gcode_line)

    movement = None
    if command == GCode.EXTRUDE:
        extruder.from_gcode(gcode_line)
    elif command == GCode.MOVE:
        movement = cur.gcode_move(gcode_line)

    #don't treat anything as real until we see the first layer marker
    if layer_num is None:
        match = layer_begin.match(gcode_line)

        if match is not None:
            layer_num = 0
            out = svg("Layer "+str(layer_num))
            stats = StatsCollector(layer_num)
        continue

    if movement is None:
        continue

    if movement.layer_change() > 0:
        out.save(layer_filename(layer_num))
        layer_num += 1
        out = svg("Layer "+str(layer_num))

        stats.write()
        stats.new_layer(layer_num)
    else:
        myline = movement.toSVG(extruder.getStyle())
        if myline is None:
            raise Exception("line is being returned as None")
        out.addElement(myline)

        if extruder.is_extruding():
            stats.add_extrude(movement)
        else:
            stats.add_move(movement)

out.save(layer_filename(layer_num))
    



