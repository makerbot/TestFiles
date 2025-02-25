#!usr/bin/python

import os
import sys
import argparse
import slicer_gcode_svg

TOTALS = '___TOTALS___'

class GcodeStat(object):
    def __init__(self):
        self.tally = slicer_gcode_svg.StatTally()

def slice_visualize(gcodename, gcodefile, outputdir, statsfile = None, statsdict = None):
    tally = slicer_gcode_svg.runvisualizer(['slicer_gcode_svg.py', gcodefile, outputdir])
    if tally is None:
        #raise an exception, we failed to slice!
        return
    filesize = os.stat(gcodefile).st_size
    if statsfile is not None:
        statsfile.write(gcodename + '\n')
        size_str = "%0.2f" % (float(filesize)/1048576)
        statsfile.write("      "+str("File Size (MB): ").ljust(24)
                           + "        " + size_str + '\n')  
        tally.write_text(statsfile, 0)
    if statsdict is not None:
        if gcodename not in statsdict:
            statsdict[gcodename]=dict()
        statsdict[gcodename]['tally'] = tally
        statsdict[gcodename]['size'] = filesize
        if TOTALS not in statsdict:
            statsdict[TOTALS]=dict()
        if 'tally' not in statsdict[TOTALS]:
            statsdict[TOTALS]['tally'] = slicer_gcode_svg.StatTally()
        if 'size' not in statsdict[TOTALS]:
            statsdict[TOTALS]['size'] = 0
        statsdict[TOTALS]['size'] += filesize
        for (key, value) in statsdict[TOTALS]['tally'].__dict__.items():
            statsdict[TOTALS]['tally'].__dict__[key]+=tally.__dict__[key]

def gather_stats(argv=None, statsdict=dict()):
    parser=argparse.ArgumentParser(
        description="")
    #MONKEY PATCH BEGIN
    def argparse_error_override(message):
        parser.print_help()
        parser.exit(2)
    parser.error=argparse_error_override
    #MONKEY PATCH END
    parser.add_argument(
        'INPUT_PATH',
        help='top folder containing input gcode files - parsed recursively')
    parser.add_argument(
        'OUTPUT_PATH',
        nargs='?',
        help='top folder where to place generated stats and visualizations',
        default=None)
    args = []
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    
    input_dir=os.path.abspath(args.INPUT_PATH)
    output_dir=(input_dir if args.OUTPUT_PATH is None else 
                os.path.abspath(args.OUTPUT_PATH))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    stats_filename = 'gcodestats.txt'
    stats_filepath = os.path.join(output_dir, stats_filename)
    stats_fh = open(stats_filepath, 'w')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for dirtuple in os.walk(input_dir):
        for filename in dirtuple[2]:
            (root, ext) = os.path.splitext(filename)
            if ext==".gcode":
                gcodename=os.path.join(dirtuple[0], root)
                filepath=os.path.join(dirtuple[0], filename)
                gcodename
                outputname=os.path.join(
                    output_dir, 
                    dirtuple[0][len(input_dir)+1:],
                    root)
                print ""
                print "**"+ str("VISUALIZING " + root).center(67) +"**"
                print ""
                slice_visualize(gcodename, filepath, outputname, 
                                statsfile = stats_fh, statsdict = statsdict)
    if TOTALS in statsdict:
        stats_fh.write(TOTALS + '\n')
        size_str = "%0.2f" % (float(statsdict[TOTALS]['size'])/1048576)
        stats_fh.write("      "+str("File Size (MB): ").ljust(24)
                           + "        " + size_str + '\n')  
        statsdict[TOTALS]['tally'].write_text(stats_fh, 0)
    return 0
                                
def main(argv=None):
    return gather_stats(argv)
    
if __name__=="__main__":
    sys.exit(main())