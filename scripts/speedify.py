#!/usr/bin/python

import argparse
import math
import zipfile
import json

parser = argparse.ArgumentParser(
        description = 'Modify the speeds of commands based on which quadrant '
        'they occupy. Quadrant numbering starts at 0 in the upper right and '
        'increases going counterclockwise')

parser.add_argument('S0', type = float, help = 'Speed of upper right box in mm')
parser.add_argument('S1', type = float, help = 'Speed of upper left box in mm')
parser.add_argument('S2', type = float, help = 'Speed of lower left box in mm')
parser.add_argument('S3', type = float, help = 'Speed of lower right box in mm')
parser.add_argument('FILE', type = str, help = 'File name of the .makerbot file to read')
parser.add_argument('OUT', type = str, help = 'File name of the  .makerbot file to write')

args = parser.parse_args()

with zipfile.ZipFile(args.FILE) as makerbot:
    toolpath = json.load(makerbot.open('print.jsontoolpath'))

for elem in toolpath:
    command = elem['command']
    if command['function'] != 'move':
        continue
    elif 'Infill' not in command['tags'] and 'Inset' not in command['tags']:
        continue
    else:
        x = command['parameters']['x']
        y = command['parameters']['y']
        if x >= 0 and y >= 0:
            s = args.S0
        elif x < 0 and y >= 0:
            s = args.S1
        elif x < 0 and y < 0:
            s = args.S2
        else:
            s = args.S3
        command['parameters']['feedrate'] = s

with zipfile.ZipFile(args.FILE, 'r') as makerbot, \
        zipfile.ZipFile(args.OUT, 'w') as ofile:
    for elem in makerbot.infolist():
        if elem.filename == 'print.jsontoolpath':
            ofile.writestr(elem, json.dumps(toolpath, indent = 4,
                    sort_keys = True))
        else:
            ofile.writestr(elem, makerbot.open(elem).read())


