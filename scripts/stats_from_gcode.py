#!usr/bin/python

import os
import sys
import argparse
import slicer_gcode_svg

class GcodeStat(object):
    def __init__(self):
        self.tally = slicer_gcode_svg.StatTally()

def slice_visualize(gcodename, gcodefile, outputdir, statsfile = None, statsdict = None):
    tally = slicer_gcode_svg.runvisualizer(['slicer_gcode_svg.py', gcodefile, outputdir])
    if tally is None:
        #raise an exception, we failed to slice!
        return
    if statsfile is not None:
        statsfile.write(gcodename + '\n')
        tally.write_text(statsfile, 0)
    if statsdict is not None:
        if gcodename not in statsdict:
            statsdict[gcodename]=dict()
        statsdict[gcodename]['tally'] = tally
    

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
                slice_visualize(gcodename, filepath, outputname, 
                                statsfile = stats_fh, statsdict = statsdict)
    return 0
                                
def main(argv=None):
    return gather_stats(argv)
    
if __name__=="__main__":
    sys.exit(main())