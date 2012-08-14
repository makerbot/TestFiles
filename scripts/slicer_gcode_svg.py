#!/usr/bin/python

import os
import sys
import re
import pysvg.structure
import pysvg.shape
import pysvg.builders
import pysvg.text
from math import sqrt


gcode_file = ''
dump_dir = './'
factor = 10.0
extruder_mode = 1

svg_dir = 'svg/'

extrude_style = pysvg.builders.StyleBuilder()
extrude_style.setStrokeWidth(.2 * factor)
extrude_style.setStroke('red')

move_style = pysvg.builders.StyleBuilder()
move_style.setStrokeWidth(.2 * factor)
move_style.setStroke('blue')

retract_style = pysvg.builders.StyleBuilder()
retract_style.setStroke('blue')
retract_style.setFilling('blue')

extract_style = pysvg.builders.StyleBuilder()
extract_style.setStroke('red')
extract_style.setFilling('red')

layer_begin = re.compile('^\((<layer>|Slice) [\d.]+.*\)$')

def layer_filename(layer_num):
    return dump_dir+svg_dir+'layer_'+str(layer_num)+'.svg'

class Coord(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, copy = None):
        if copy is None:
            self.x = x
            self.y = y
            self.z = z
        else:
            self.x = copy.x
            self.y = copy.y
            self.z = copy.z
    def copy(self, other):
        self.x = other.x
        self.y = other.y
        self.z = other.z
    def __abs__(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)
    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y, self.z - other.z)
    def __repr__(self):
        return "(" + repr(self.x) + ", " + repr(self.y) + ", " + repr(self.z) + ")"
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

def distance_linear(coord1, coord2):
    return abs(coord2 - coord1)

#represents the lowest coordinates, used when outputting to svg
minposition = Coord()

class StatTally(object):
    def __init__(self):
        self.Extruder_A_Distance = 0.0
        self.Extruder_B_Distance = 0.0
        self.Extruder_E_Distance = 0.0
        self.Total_Move_Distance= 0.0
        self.Total__Retracts = 0
        self.Total__Extracts = 0
        self.Total__Switches = 0
        self.Total_Duration= 0.0
        self.Move_Count = 0
    def write(self, html_fh, tabs = 2):
        fh = html_fh
        pretab = ""
        tab = "\t"
        for i in range(1, tabs):
            pretab += tab
        table = "<table style='font-family: monospace;'>\n"
        tablec = "</table>\n"
        tr = "<tr>\n"
        trc = "</tr>\n"
        td = "<td>"
        tdc = "</td>\n"
        nbsp = '&nbsp'
        self.write_generic(fh, pretab, tab, 
                      table, tablec, 
                      tr, trc, td, tdc, 6, nbsp)
    def write_text(self, text_fh, tabs = 0):
        fh = text_fh
        pretab = ""
        tab = "  "
        for i in range(1, tabs):
            pretab += tab
        table = "\n"
        tablec = "\n\n"
        tr = ""
        trc = "\n"
        td = ""
        tdc = ""
        nbsp = ""
        self.write_generic(fh, pretab, tab, 
                      table, tablec, 
                      tr, trc, td, tdc, 0, nbsp)
    def write_generic(self, fh, 
                      pretab, tab, 
                      table, tablec, 
                      tr, trc, 
                      td, tdc, spacecount, nbsp): 
        fh.write(pretab + table)
        for key, value in sorted(self.__dict__.iteritems()):
            fh.write(pretab + tab + tr)
            fh.write(pretab + tab + tab + td)
            fh.write((str(key)+':').ljust(24))
            fh.write(tdc)
            fh.write(pretab + tab + tab + td)
            spacecount = 0
            while spacecount < spacecount:
                fh.write(nbsp)
                spacecount += 1
            fh.write(tdc)
            fh.write(pretab + tab + tab + td)
            fh.write(str(value).ljust(24))
            fh.write(tdc)
            fh.write(pretab + tab + trc)
        fh.write(pretab + tablec)
        
        

class Gantry(object):
    def __init__(self):
        self.position = Coord()
        self.A = 0.0
        self.B = 0.0
        self.E = 0.0
        self.isExtruding = False
        #how much movement while extruding with A
        self.AdistanceAccum = 0.0
        #how much movement while extruding with B
        self.BdistanceAccum = 0.0
        #how much movement while extruding with E
        self.EdistanceAccum = 0.0
        #how much movement without extruding
        self.DryAccum = 0.0
        #how many times we retracted
        self.RetractAccum = 0
        #opposite of above
        self.ExtractAccum = 0
        #how many times we switched any extruder on
        self.SwitchAccum = 0
        #how long are we moving on this layer
        self.DurationAccum = 0.0
        #information regarding z height
        self.CurrentZ = 0.0
        self.SeenLayer = False
        self.CurrentLayer = 0
        self.LayerEncounteredOnce = False
        self.MoveCount = 0
        #finally, that thing which totals things
        self.tally = StatTally()
    def flush_accumulators(self, svg_object):
        '''Output accumulator values to svg and reset them.
        '''
        table = "<g transform='translate(32, 32)'>\n"
        tablec = "</g>\n"
        
        def tr(y):
            return "\t<text font-family='monospace' transform='translate(0," + str(y) + ")'>\n"
        
        trc = "\t</text>\n"
        def td(x):
            return "\t\t<tspan x='" + str(x) + "'>\n\t\t"
        tdc = "\t\t</tspan>\n"
        htmltable =     [["Current Layer # : ", str(self.CurrentLayer), "(count)"],
                         ["Current Layer Z : ", str(self.CurrentZ), "(mm)"], 
                         ["Sum of Distance : ", str(self.AdistanceAccum +
                                                  self.BdistanceAccum +
                                                  self.EdistanceAccum +
                                                  self.DryAccum), "(mm)"],
                         ["Ext. A Distance : ", str(self.AdistanceAccum), "(mm)"],
                         ["Ext. B Distance : ", str(self.BdistanceAccum), "(mm)"],
                         ["Ext. E Distance : ", str(self.EdistanceAccum), "(mm)"],
                         ["Moving Distance : ", str(self.DryAccum), "(mm)"],
                         ["Travel Duration : ", str(self.DurationAccum), "(sec)"],
                         ["Observed Toggle : ", str(self.SwitchAccum), "(count)"],
                         ["Expected Toggle : ", str(self.RetractAccum + self.ExtractAccum), "(count)"],
                         ["Retractions Num : ", str(self.RetractAccum), "(count)"],
                         ["Extractions Num : ", str(self.ExtractAccum), "(count)"],
                         ["Movements Count : ", str(self.MoveCount), "(count)"]]
        self.CurrentLayer += 1
        y = 0
        htmlstring = table
        for row in htmltable:
            htmlstring += tr(y)
            y+=18
            x = 0
            for col in row:
                htmlstring += td(x)
                x += 150
                htmlstring += col
                htmlstring += "\n"
                htmlstring += tdc
            htmlstring += trc
        htmlstring += tablec
        svg_object.appendTextContent(htmlstring)
        self.isExtruding = False
        
        self.tally.Extruder_A_Distance += self.AdistanceAccum
        self.tally.Extruder_B_Distance += self.BdistanceAccum
        self.tally.Extruder_E_Distance += self.EdistanceAccum
        self.tally.Total_Move_Distance+= self.DryAccum
        self.tally.Total__Retracts += self.RetractAccum
        self.tally.Total__Extracts += self.ExtractAccum
        self.tally.Total__Switches += self.SwitchAccum
        self.tally.Total_Duration+= self.DurationAccum
        self.tally.Move_Count += self.MoveCount        
        
        self.AdistanceAccum = 0.0
        self.BdistanceAccum = 0.0
        self.EdistanceAccum = 0.0
        self.DryAccum = 0.0
        self.RetractAccum = 0
        self.ExtractAccum = 0
        self.SwitchAccum = 0
        self.DurationAccum = 0.0
        self.MoveCount = 0
        
    def process_splitcode(self, position, A, B, E, F, Layer, Line, svg_object):
        '''Process new position and extrusion axes.
        '''

        self.MoveCount += 1
        
        retbool = False
        extrudebool = False
        retractbool = False
        extractbool = False
        startpos = self.position - minposition
        endpos = position - minposition
        myline = pysvg.shape.line(startpos.x * factor, startpos.y * factor,
                      endpos.x * factor, endpos.y * factor)
        distance = distance_linear(position, self.position)
        filament_distance = abs(A - self.A) + abs(B-self.B) + abs(E-self.E)
        if F is not None:
            self.DurationAccum += (filament_distance) / (F / 60)
            self.DurationAccum += (distance) / (F / 60)
        #increment appropriate values
        if A != self.A:
            extrudebool = True
            retractbool = retractbool or A < self.A
            extractbool = extractbool or ((not retractbool) and distance == 0.0)
            self.AdistanceAccum += distance
        if B != self.B:
            extrudebool = True
            retractbool = retractbool or B < self.B
            extractbool = extractbool or ((not retractbool) and distance == 0.0)
            self.BdistanceAccum += distance
        if E != self.E:
            extrudebool = True
            retractbool = retractbool or E < self.E
            extractbool = extractbool or ((not retractbool) and distance == 0.0)
            self.EdistanceAccum += distance
        if self.LayerEncounteredOnce:
            if position.z != self.CurrentZ:
                if self.SeenLayer:
                    retbool = True
                    self.SeenLayer = False
                else:
                    print ""
                    print ("Z change from " + str(self.CurrentZ) + 
                           " to " + str(position.z) + " without layer label")
                    print Line
                    self.CurrentZ = position.z
                    #exit(1)
        else:
            self.CurrentZ = position.z
        if extrudebool != self.isExtruding:
            self.isExtruding = extrudebool
            self.SwitchAccum += 1
        if retractbool:
            self.RetractAccum += 1
            mycircle = pysvg.shape.circle(endpos.x * factor, endpos.y * factor, 0.25 * factor)
            mycircle.set_style(retract_style.getStyle())
            svg_object.addElement(mycircle)
        if extractbool:
            self.ExtractAccum += 1
            mycircle = pysvg.shape.circle(endpos.x * factor, endpos.y * factor, 0.25 * factor)
            mycircle.set_style(extract_style.getStyle())
            svg_object.addElement(mycircle)
        if Layer:
            self.LayerEncounteredOnce = True
            self.SeenLayer = True
        elif extrudebool:
            #emit an extrusion move
            myline.set_style(extrude_style.getStyle())
            svg_object.addElement(myline)
        elif position.x != self.position.x or position.y != self.position.y:
            #emit a nonextudsion move and update dry distance
            myline.set_style(move_style.getStyle())
            svg_object.addElement(myline)
            self.DryAccum += distance
        if retbool:
            self.flush_accumulators(svg_object)
            self.CurrentZ = position.z
        self.position = position
        self.A = A
        self.B = B
        self.E = E
        return retbool
    def process_code(self, gcode_dict, svg_object):
        '''Process one line of gcode.
        
        Process the gcode and emit the appropriate line to the svg file. If
        not layer change, return false. Otherwise return true.
        '''
        position = Coord(copy = self.position)
        A = self.A
        B = self.B
        E = self.E
        F = None
        Layer = None
        Line = None
        ValidBool = False
        if 'X' in gcode_dict:
            position.x = gcode_dict['X']
            ValidBool = True
        if 'Y' in gcode_dict:
            position.y = gcode_dict['Y']
            ValidBool = True
        if 'Z' in gcode_dict:
            position.z = gcode_dict['Z']
            ValidBool = True
        if 'A' in gcode_dict:
            A = gcode_dict['A']
            ValidBool = True
        if 'B' in gcode_dict:
            B = gcode_dict['B']
            ValidBool = True
        if 'E' in gcode_dict:
            E = gcode_dict['E']
            ValidBool = True
        if 'F' in gcode_dict:
            F = gcode_dict['F']
            ValidBool = True
        if 'Layer' in gcode_dict:
            Layer = gcode_dict['Layer']
            ValidBool = True
        if 'Line' in gcode_dict:
            Line = gcode_dict['Line']
        if not ValidBool:
            return False
        return Gantry.process_splitcode(self, position, A, B, E, F, Layer, Line, svg_object)
        

def code_dict_from_line(gcode_line, line_num = -1):
    retDict = dict()
    gl = gcode_line.split()
    for word in gl:
        if len(word) < 2 or word[0] not in 'ABEFGMXYZ':
            break
        retDict[word[0]] = float(word[1:])
    match = layer_begin.match(gcode_line)
    if match is not None:
        retDict['Layer'] = gcode_line
    retDict['Line'] = str(line_num) + ": \t" + str(gcode_line)
    return retDict

#ugly global hack
last_s3g_z = None

def code_dict_from_s3g(s3gline, line_num = -1):
    global last_s3g_z
    retDict = dict()
    if (s3gline[:6] == '[139, ' or
        s3gline[:6] == '[142, ') and s3gline[-1] == ']':
        s3gline = s3gline[6:-1]
        args = s3gline.split(', ')
        codes = 'XYZABF'
        for i in range(len(codes)):
            retDict[codes[i]] = float(args[i])
        if last_s3g_z != retDict['Z']:
            last_s3g_z = retDict['Z']
            retDict['Layer'] = s3gline
        retDict['Line'] = str(line_num) + ": \t" + str(s3gline)
    return retDict

def make_html(svgList, tally, title):
    if title is None:
        print "Current file name is not valid"
        return
    htmlname = dump_dir + 'index.html'
    print "Outputting index.html to " + htmlname
    print "Base directory is " + dump_dir
    fh = open(dump_dir + 'index.html', "w")
    fh.write("<html>\n")
    #head
    fh.write("\t<head>\n")
    fh.write("\t\t<title>" + title + "</title>\n");
    fh.write("\t</head>\n")
    #end head
    #body
    fh.write("\t<body>\n")
    #tally
    tally.write(fh, 2)
    #table
    fh.write("\t\t<table>\n")
    for svg in svgList:
        svgmod = svg[svg.find(dump_dir) + len(dump_dir):]
        #print "Indexing: \t" + svgmod
        fh.write("\t\t\t<tr>\n")
        #file name
        fh.write("\t\t\t\t<td>")
        fh.write("<a href = \"" + svgmod + "\">")
        fh.write(svgmod)
        fh.write("</a>")
        fh.write("</td>\n")
        #preview
        fh.write("\t\t\t\t<td>")
        #fh.write("<a href = \"" + svg + "\">")
        #fh.write("<object height=\"32\" width=\"48\" type=\"image/svg+xml\" data = \"" + svgmod + "\" >")
        #fh.write(svg)
        #fh.write(" alt text</object>")
        #fh.write("</a>")
        fh.write("</td>\n")
        fh.write("\t\t\t</tr>\n")
    fh.write("\t\t</table>\n")
    #end table
    fh.write("\t</body>\n")
    #end body
    fh.write("</html>\n")
    fh.close()

################################################################################

def runvisualizer(argv=None):
    
    if argv is None:
        argv = sys.argv
        
    lsa = len(argv)
    print "slice_analyzer: ", lsa, " arguments\n";

    global gcode_file
    global dump_dir
    global factor
    global extuder_mode
    
    for arg in range(0, lsa):
        print "#", arg, ": \t", argv[arg];

    if lsa < 2:
        print """

    Slice analyzer
    Usage: 
        slice_analyzer.py GCODE_FILE [OUTPUT_DIRECTORY] [SCALE_FACTOR] [EXTRUDER_MODE]
        
        where:
            GCODE_FILE       : the input file to analyze
            OUTPUT_DIRECTORY : the directory where all text and svg files are stored
            SCALE_FACTOR     : SVG scale factor (10 recommended)
            EXTRUDER_MODE    : not used? (integer)
    """
        return -1
    if lsa >= 2:
        gcode_file = argv[1];
    if lsa >= 3:
        dump_dir = argv[2];
        if dump_dir == '':
            dump_dir = './'
        elif dump_dir[-1] != '/':
            dump_dir = dump_dir + '/'
    if lsa >= 4:
        factor = float(argv[3]);
    if lsa >= 5:
        extruder_mode = int(argv[4]);

    if not os.path.exists(dump_dir+svg_dir):
        os.makedirs(dump_dir+svg_dir)

    translate = None

    print "Input File: \t" + str(gcode_file)
    print "Output Directory: \t" + str(dump_dir)
    print "Scaling Factor: \t" + str(factor)
    print gcode_file[-5:]
    if gcode_file[-5:].lower() == 'gcode':
        translate = code_dict_from_line
    else:
        translate = code_dict_from_s3g

    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)
    if not os.path.exists(dump_dir + svg_dir):
        os.makedirs(dump_dir + svg_dir)

    gcode_fh = open(gcode_file, "r")
    svgList = []

    #find the bounds of the object
    seenLayer = False
    for gcode_line in gcode_fh.readlines():
        gcode_line = gcode_line.rstrip()
        code_dict = translate(gcode_line)
        if 'Layer' in code_dict:
            seenLayer = True
        if seenLayer:
            if 'X' in code_dict:
                minposition.x = min([minposition.x, code_dict['X']])
            if 'Y' in code_dict:
                minposition.y = min([minposition.y, code_dict['Y']])
    minposition.x -= 32/factor
    minposition.y -= 256/factor
    print "Minimum Coordinates: \t" + str(minposition)

    gcode_fh.close()
    gcode_fh = open(gcode_file, "r")

    gantry = Gantry()
    layer_num = 0

    svg_filename = layer_filename(layer_num)
    svg_object = pysvg.structure.svg("Layer " + str(layer_num))
    line_num = 1
    print "Starting processing of layers"
    for gcode_line in gcode_fh.readlines():
        gcode_line = gcode_line.strip()
        if gantry.process_code(translate(gcode_line, line_num),svg_object):
            svg_object.save(svg_filename)
            svgList.append(svg_filename)
            sys.stdout.write('.')
            sys.stdout.flush()
            layer_num += 1
            svg_filename = layer_filename(layer_num)
            svg_object = pysvg.structure.svg("Layer " + str(layer_num))
        line_num += 1
    gantry.flush_accumulators(svg_object)
    svg_object.save(svg_filename)
    svgList.append(svg_filename)

    print ""

    print "Layers Parsed: \t" + str(layer_num)
    print "Starting generation of index"

    make_html(svgList, gantry.tally, gcode_file)
    return gantry.tally

def main(argv = None):
    return (1 if runvisualizer(argv) is None else 0)
    

if __name__ == "__main__":
    sys.exit(main())
        




