#!usr/bin/python

import os
import sys
import subprocess
import argparse

def print_stl(filepath, filename, mg_command, output_dir):
    filename = filename[:-4] + ".gcode"
    output_filepath = os.path.join(output_dir, filename)
    command = mg_command + " -o " + output_filepath + " " + filepath
    print command
    return os.system(command)
    

def main(argv=None):
    parser=argparse.ArgumentParser(
        description="Slices files with MG and puts them in a directory")
    #MONKEY PATCH BEGIN
    def argparse_error_override(message):
        parser.print_help()
        parser.exit(2)
    parser.error=argparse_error_override
    #MONKEY PATCH END
    parser.add_argument(
        'MG_PATH',
        help='path to miracle_grue binary executable file')
    parser.add_argument(
        'MG_CONFIG',
        help='path to configuration file for Miracle Grue')
    parser.add_argument(
        'INPUT_PATH',
        help='top folder containing input stl files - parsed recursively')
    parser.add_argument(
        'OUTPUT_PATH',
        nargs='?',
        help='top folder where to place generated files',
        default=None)
    args = []
    args = parser.parse_args()
    
    mg_command=args.MG_PATH
    mg_config=args.MG_CONFIG
    input_dir=args.INPUT_PATH
    output_dir=(input_dir if args.OUTPUT_PATH is None else args.OUTPUT_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for dirtuple in os.walk(input_dir):
        for filename in dirtuple[2]:
            (root, ext) = os.path.splitext(filename)
            if ext==".stl":
                filepath=os.path.join(dirtuple[0], filename)
                outputname=os.path.join(
                    output_dir, 
                    dirtuple[0][len(input_dir):],
                    root+".gcode")
                subprocess.check_call(
                    [mg_command,
                     '-c', mg_config,
                     '-o', outputname,
                     filepath])
    
if __name__=="__main__":
    sys.exit(main())
