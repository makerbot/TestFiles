#!usr/bin/python

import os
import sys
import subprocess
import argparse
import time

TOTALS = '___TOTALS___'

def mg_slice_model(binary_dir, config_dir, input_dir, output_dir):
    argslist = [binary_dir, '-c', config_dir, 
                '-o', output_dir, input_dir]
    sys.stdout.write('\nSlicer command:\n')
    for curarg in argslist:
        sys.stdout.write(curarg + ' ')
    sys.stdout.write('\n\n')
    subprocess.check_call(argslist)

def skein_slice_model(binary_dir, config_dir, input_dir, output_dir):
    print("inside skein slice")
    import skeinforge
    argslist = ['skeinforge.py', binary_dir, config_dir, input_dir, output_dir]
    skeinforge.slice(argslist)

def dispatch_slice_model(binary_dir, config_dir, input_dir, output_dir):
    """Determine which slicer to use, then use it to slice model"""
    if 'skeinforge' in binary_dir.lower():
        skein_slice_model(binary_dir, config_dir, input_dir, output_dir)
    else:
        mg_slice_model(binary_dir, config_dir, input_dir, output_dir)

def batch_slice(argv=None):
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
        type=os.path.abspath, 
        help='path to slicer executable file')
    parser.add_argument(
        'SLICER_CONFIG',
        type=os.path.abspath, 
        help='path to slicer configuration file')
    parser.add_argument(
        'INPUT_PATH',
        type=os.path.abspath, 
        help='top folder containing input stl files - parsed recursively')
    parser.add_argument(
        'OUTPUT_PATH',
        type=os.path.abspath, 
        nargs='?',
        help='top folder where to place generated files',
        default=None)
    args = []
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    
    slicer_command=os.path.abspath(args.SLICER_PATH)
    slicer_config=os.path.abspath(args.SLICER_CONFIG)
    input_dir=os.path.abspath(args.INPUT_PATH)
    output_dir=(input_dir if args.OUTPUT_PATH is None else 
                os.path.abspath(args.OUTPUT_PATH))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    statsdict = dict()
    for dirtuple in os.walk(input_dir):
        for filename in dirtuple[2]:
            (root, ext) = os.path.splitext(filename)
            if ext==".stl":
                filepath=os.path.join(dirtuple[0], filename)
                filepath=os.path.abspath(filepath)
                endpath=dirtuple[0][len(input_dir)+1:]
                gcodepath=os.path.join(output_dir, endpath)
                if not os.path.exists(gcodepath):
                    os.makedirs(gcodepath)
                gcodename=os.path.join(gcodepath, root)
                gcodename=os.path.abspath(gcodename)
                outputname=gcodename + '.gcode'
                print("")
                print("**"+ str("SLICING " + root).center(67) +"**")
                print("")
                starttime = time.clock()
                dispatch_slice_model(slicer_command, slicer_config, filepath, outputname)
                endtime = time.clock()
                duration = endtime - starttime
                if gcodename not in statsdict:
                    statsdict[gcodename] = dict()
                statsdict[gcodename]['time'] = duration
                statsdict[gcodename]['size'] = os.stat(outputname).st_size
                print("Slicing file " + gcodename + " took " + str(duration) + " seconds")
                if TOTALS not in statsdict:
                    statsdict[TOTALS]=dict()
                    statsdict[TOTALS]['time'] = 0
                    statsdict[TOTALS]['size'] = 0
                statsdict[TOTALS]['time'] += statsdict[gcodename]['time']
                statsdict[TOTALS]['size'] += statsdict[gcodename]['size']
    return statsdict
                

def main(argv=None):
    return (1 if batch_slice(argv) is None else 0)

if __name__=="__main__":
    sys.exit(main())
