#!/usr/bin/python

import fileinput
import json

datastr = '\n'.join(line for line in fileinput.input())
datajson = json.loads(datastr)

state = dict({'x' : 0, 'y' : 0, 'z' : 0, 'a' : 0})

for element in datajson:
    if 'command' not in element:
        continue
    command = element['command']
    if 'function' not in command or command['function'] != 'move':
        continue
    params = command['parameters']
    values = []
    for axis in 'xyza':
        if command.get('metadata', dict()).get('relative', dict()).get(axis, False):
            state[axis] += params[axis]
        else:
            state[axis] = params[axis]
        values.append((axis.upper(), state[axis],))
    values.append(('F', 60 * params['feedrate'],))
    if 'tags' in command:
        values.append((';', ' '.join(command['tags'])))
    print ' '.join(['G1'] + [k+str(v) for (k, v) in values])


