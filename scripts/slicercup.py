#!usr/bin/python

import os
import sys
import argparse
import stats_from_gcode
import batch_slice

def mg_slicercup_func(argv=None):
    parser=argparse.ArgumentParser(
        description="Slices files with MG and puts them in a directory")
    #MONKEY PATCH BEGIN
    def argparse_error_override(message):
        parser.print_help()
        parser.exit(2)
    parser.error=argparse_error_override
    #MONKEY PATCH END
    parser.add_argument(
        'SLICER_PATH',
        help='path to slicer executable file')
    parser.add_argument(
        'SLICER_CONFIG',
        help='path to slicer configuration file')
    parser.add_argument(
        'STL_PATH',
        help='top folder containing input stl files - parsed recursively')
    parser.add_argument(
        'GCODE_PATH',
        nargs='?',
        help='top folder where to place generated files',
        default=None)
    parser.add_argument(
        'STAT_PATH',
        nargs='?',
        help='top folder where to place generated files',
        default=None)
    args = []
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    
    slicer_command=os.path.abspath(args.SLICER_PATH)
    slicer_config=os.path.abspath(args.SLICER_CONFIG)
    stl_dir=os.path.abspath(args.STL_PATH)
    gcode_dir=(stl_dir if args.GCODE_PATH is None else 
               os.path.abspath(args.GCODE_PATH))
    stat_dir=(gcode_dir if args.STAT_PATH is None else 
              os.path.abspath(args.STAT_PATH))
    print "***********************************************************************"
    print "**                           BEGIN SLICING                           **"
    print "***********************************************************************"
    statsdict = batch_slice.batch_slice([slicer_command, slicer_config, 
                                              stl_dir, gcode_dir])
    print "***********************************************************************"
    print "**                         BEGIN VISUALIZING                         **"
    print "***********************************************************************"
    stats_from_gcode.gather_stats([gcode_dir, stat_dir], statsdict)

    stats_filename = 'gcodestats.txt'
    stats_filepath = os.path.join(stat_dir, stats_filename)
    stats_fh = open(stats_filepath, 'w')
    
    print "***********************************************************************"
    print "**                           COLLATE STATS                           **"
    print "***********************************************************************"
    
    for (model, stats) in statsdict.items():
        stats_fh.write(model + '\n')
        if 'time' in stats:
            duration = stats['time']
            hours = int(duration/3600)
            duration -= 3600*hours
            minutes = int(duration/60)
            duration -= 60*minutes
            seconds = duration
            duration_str = "%02i:%02i:%05.2f" % (hours,minutes,seconds)
            stats_fh.write("      "+str("Slice Time (hh:mm::ss.ss): ").ljust(24)
                           + "        " + duration_str + '\n')
        if 'size' in stats:
            size_str = "%0.2f" % float(stats['size'])/1048576
            stats_fh.write("      "+str("File Size (MB): ").ljust(24)
                           + "        " + size_str + '\n')
        if 'tally' in stats:
            stats['tally'].write_text(stats_fh, 0)
    print "***********************************************************************"
    print "**                          SCRIPT COMPLETE                          **"
    print "***********************************************************************"
    return 0

    

def main(argv=None):
    return mg_slicercup_func(argv)

if __name__=="__main__":
    sys.exit(main())
