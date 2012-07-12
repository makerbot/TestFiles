import os
import sys
import re
import pysvg.structure
import pysvg.shape
import pysvg.builders
import math

move_style = pysvg.builders.StyleBuilder()
move_style.setStroke('blue')

point_re = re.compile('\[(-?\d+(\.\d+)?), (-?\d+(\.\d+)?)\]')

#a point is a tuple of floats
def pointlist_to_svg(point_list, svg_object):
    #print "Outputting point list..."
    if len(point_list) < 3:
        return
    startpoint = None
    lastpoint = None
    for point in point_list:
        #print point
        if startpoint is None:
            startpoint = point
            lastpoint = point
        else:
            line = pysvg.shape.line(lastpoint[0], lastpoint[1], point[0], point[1])
            line.set_style(move_style.getStyle())
            svg_object.addElement(line)
            lastpoint = point
    line = pysvg.shape.line(lastpoint[0], lastpoint[1], startpoint[0], startpoint[1])
    line.set_style(move_style.getStyle())
    svg_object.addElement(line)
    return

def point_list_list_offset(point_list_list, offsetpoint):
    minpoint = (0.0, 0.0)
    for point_list in point_list_list:
        for point in point_list:
            if point[0] < minpoint[0]:
                minpoint = (point[0], minpoint[1])
            if point[1] < minpoint[1]:
                minpoint = (minpoint[0], point[1])
    offset = (offsetpoint[0] - minpoint[0], offsetpoint[1] - minpoint[1])
    print "Minimum Point: " + str(minpoint)
    print "Offset: " + str(offset)
    for point_list_index, point_list in enumerate(point_list_list):
        for point_index, point in enumerate(point_list):
            point_list_list[point_list_index][point_index] = (point[0] + offset[0], point[1] + offset[1])
    

def main(argv=None):

    global move_style
    
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        print """
        Loop Visualizer
        Usage:
            loop_visualizer.py INPUT_FILE [OUTPUT_FILE] [SCALE_FACTOR]

            where:
                INPUT_FILE    : the input file to visualize
                OUTPUT_FILE   : the svg file to be output
                SCALE_FACTOR  : SVG scale factor
        """
        return -1
    input_file = argv[1]
    output_file = input_file + ".svg"
    if len(argv) > 2:
        output_file = argv[2]
    scale_factor = 30
    if len(argv) > 3:
        scale_factor = int(argv[3])

    print "Input File:  \t\t" + str(input_file)
    print "Output File: \t\t" + str(output_file)
    print "Scaling Factor: \t" + str(scale_factor)

    move_style.setStrokeWidth(.5 * math.sqrt(scale_factor))

    svg_object = pysvg.structure.svg(output_file)
    point_list_list = []
    point_list = []
    input_fh = open(input_file, "r")
    
    for line in input_fh.readlines():
        line = line.strip()
        rematch = point_re.match(line)
        if rematch is None:
            point_list_list.append(point_list)
            point_list = []
        else:
            #convert current line to a point tuple scaled by scale_factor
            #print rematch.groups()
            strpoint0 = rematch.group(1)
            strpoint1 = rematch.group(3)
            strpoint = (strpoint0, strpoint1)
            #print strpoint
            point = (float(strpoint[0]) * scale_factor, float(strpoint[1]) * scale_factor)
            point_list.append(point)

    point_list_list.append(point_list)

    point_list_list_offset(point_list_list, (3 * scale_factor, 3 * scale_factor))

    #print point_list_list

    for point_list_sub in point_list_list:
        pointlist_to_svg(point_list_sub, svg_object)

    svg_object.save(output_file)

    
    
    return 0
    

if __name__ == "__main__":
    sys.exit(main())
