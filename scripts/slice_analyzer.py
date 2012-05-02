#!/usr/bin/python

import os
import sys
import re
from pysvg.structure import svg
from pysvg.shape import line
from pysvg.builders import StyleBuilder


layer_begin = re.compile('^\((<layer>|Slice) [\d.]+.*\)$')
gcode_move = re.compile('G1 (X(-?\d+\.?\d*))? (Y(-?\d+\.?\d*))? (Z(-?\d+\.?\d*))? (F(\d+\.?\d*))?')
gcode_command_code = re.compile('([A-Z]\d+)(\s|$)')

gcode_file = sys.argv[1]
dump_dir = sys.argv[2]
factor = int(sys.argv[3])
extruder_mode = int(sys.argv[4])

min_x = 0
min_y = 0

def layer_filename(layer_num):
    return dump_dir+'/layer_'+str(layer_num)+'.svg'


(MOVE, EXTRUDE) = range(2)
    
def code_from_line(gcode_line):
    match = gcode_command_code.match(gcode_line)

    if match is None: return None
    else: return match.group(1)
        

def line_type(gcode_line):
    code = code_from_line(gcode_line)

    if code == "G1":
        return MOVE
    if code in ("M101", "M102", "M103", "M108"):
        return EXTRUDE
    elif code is None:
        print "Not a code line: ["+ gcode_line + "]"
    else:
        print "unknown code: " + code
        return None

def parse_G1_line(gcode_line):
    match = gcode_move.match(gcode_line)
    
    if match is None:
        return None

    return [float(match.group(2)), float(match.group(4)),
            float(match.group(6)), float(match.group(8))]


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

class Position(Coord):
    def move(self, newpos, speed):
        movement = Movement(self, newpos, speed)

        myz = movement.z
        self.copy(newpos)
        return movement

    def gcode_move(self, gcode):
        values = parse_G1_line(gcode)

        if values is None: return None

        return self.move(Coord(values[0], values[1], values[2]),
                         values[3])

class Extruder(object):
    extrude_style = StyleBuilder()
    extrude_style.setStrokeWidth(.3 * factor)
    extrude_style.setStroke('red')

    move_style = StyleBuilder()
    move_style.setStrokeWidth(.3 * factor)
    move_style.setStroke('blue')

    def __init__(self):
        self.extruding = False

    def isExtruding(self):
        return self.extruding

    def from_gcode(self, gcode_line):
        code = code_from_line(gcode_line)
        if code in ("M102", "M103"):
            print "Switching off extruder"
            self.extruding = False
        elif code == "M101":
            print "Switching on extruder"
            self.extruding = True
        else:
            print "Unknown code: " + code
            

    def getStyle(self):
        if self.extruding:
            print "extrude"
            return self.extrude_style
        else:
            print "move"
            return self.move_style
        

################################################################################

gcode_fh = open(gcode_file, "r")

#find the bounds of the object
for gcode_line in gcode_fh.readlines():
    gcode_line = gcode_line.rstrip()
    values = parse_G1_line(gcode_line)

    if values is None: continue

    if values[0] < min_x: min_x = values[0]
    if values[1] < min_y: min_y = values[1]

print "min_x: " + str(min_x)
print "min_y: " + str(min_y)

gcode_fh.close()
gcode_fh = open(gcode_file, "r")

cur = Position()
out = None
layer_num = None


extruder = Extruder()

for gcode_line in gcode_fh.readlines():
    gcode_line = gcode_line.rstrip()

    command = line_type(gcode_line)

    movement = None
    if command == EXTRUDE:
        print "Extrude line: " + gcode_line
        extruder.from_gcode(gcode_line)
    elif command == MOVE:
        movement = cur.gcode_move(gcode_line)

    #don't treat anything as real until we see the first layer marker
    if layer_num is None:
        match = layer_begin.match(gcode_line)

        if match is not None:
            layer_num = 0
            out = svg("Layer "+str(layer_num))

        continue

    if movement is None:
        continue

    if movement.layer_change() > 0:
        out.save(layer_filename(layer_num))
        layer_num += 1
        out = svg("Layer "+str(layer_num))
    else:
        myline = movement.toSVG(extruder.getStyle())
        if myline is None:
            raise Exception("line is being returned as None")
        out.addElement(myline)

out.save(layer_filename(layer_num))
    



