import os
import sys
import re
import math
import argparse
import copy
import json

layer_begin = re.compile('^(\(|;)(<layer>|Slice) [\d.]+.*(\)|:)?$')
paramcodes = 'XYZFABE'
g1re = re.compile('^G1\s+(?P<param>(['+paramcodes+']-?\d+(\.\d*)?\s*)+)(?P<comment>.*)$')
paramre = re.compile('(?P<code>['+paramcodes+'])(?P<value>-?\d+(\.\d*)?)')

def formatParamDict(params, category = ''):
    '''Convert a dict into an xml-like format'''
    return reduce(lambda a,b: '%s %s=\"%s\"' % ((a,) + b), params.iteritems(), category)
    
def writeSvg(output, elements):
    '''Write elements (an iterable) to output (a file-like thing)'''
    output.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" standalone=\"no\"?>\n")
    output.write("<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\">\n")
    for element in elements:
        if element:
            output.write(element + '\n')
    output.write("</svg>\n")

def decodeCommand(command):
    '''Decode a G1 command or layer change into a dict.'''
    params = dict()
    params['line']=filter(lambda a: a!='\n',command)
    if layer_begin.match(command):
        params['layer']=True
    g1match = g1re.match(command)
    if None is not g1match:
        params['G1']=True
        data = paramre.finditer(g1match.group('param'))
        for match in data:
            params[match.group('code')] = float(match.group('value'))
    if 'layer' in params:
        sys.stdout.write('.')
        sys.stdout.flush()
    return params

def encodeCommand(command):
    '''Reconstruct a decoded command.'''
    if 'G1' in command:
        foo = lambda a,b: ('%s%s')%(a,((' '+b+str(command[b])) if b in command else ''),)
        if 'old' in command:
            return reduce(foo, paramcodes, 'OLD: %s\nNEW: G1' % (encodeCommand(command['old'])))
        else:
            return reduce(foo, paramcodes, 'G1')
    else:
        try:
            return command['line']
        except KeyError as ke:
            return ''

def interpretCommand(command):
    '''Get a style string from a preprocessed command.'''
    def speedConvert(s):
        s = (s / 5000.0) * 256.0 ** 2
        c = [256.0 ** 2, 256.0, 256.0]
        sc = [math.fmod(s, p) * 256.0/p for p in c]
        ret = [int(sci) for sci in sc]
        #print s, sc
        return ret
    def paramConvert(sc):
        return (sc[0], sc[1], sc[2], 2.0)
        
    speedParam = lambda s: paramConvert(speedConvert(s))
    
    if 'G1' in command:
        for axis in 'ABE':
            if axis in command and axis in command['old']:
                volume = command[axis] - command['old'][axis]
                break
        if volume == 0:   #travel move
            params = (0,255,0,1)
        else:
            params = speedParam(command['F'])
        return 'stroke:rgb(%s,%s,%s);stroke-width:%s' % params
    elif 'type' in command and command['type'] == 'movement':
        volume = command['volume']
        if volume == 0:   #travel move
            params = params = (0,255,0,1)
        else:
            params = speedParam(command['speed'])
        return 'stroke:rgb(%s,%s,%s);stroke-width:%s' % params
    else:
        return None
    
def parseCommands(commands):
    '''Get a list of decoded commands from the commands iterable'''
    sys.stdout.write('\nReading Commands\n')
    sys.stdout.flush()
    return [decodeCommand(command) for command in commands]
    
def dropInitCommands(commands):
    '''
        Drop all things before the first layer label in decoded commands.
        
        Returns a list containing only commands from the first layer label
    '''
    for index in range(len(commands)):
        if 'layer' in commands[index]:
            return commands[index:]
    
def offsetCommands(commands, offset = (0.0,0.0), scale=10.0):
    '''
        Make all X,Y coordinates in commands positive plus offset.
        
        commands is an iterable of decoded commands.
        offset is a coordinate pair. All commands will be moved such that 
        no command is below offset.
        scale will increase the size of things
    '''
    minimums = dict({'X':999.0, 'Y':999.0})
    maximums = dict({'X':-999.0, 'Y':-999.0})
    offset = dict({'X':offset[0], 'Y':offset[1]})
    sys.stdout.write('\nDetecting Extents\n')
    sys.stdout.flush()
    for command in commands:
        if 'layer' in command:
            sys.stdout.write('.')
            sys.stdout.flush()
        for axis in 'XY':
            if axis in command:
                minimums[axis] = min(minimums[axis],command[axis])
                maximums[axis] = max(maximums[axis],command[axis])
    print '\nMinimums:', '%s\t%s' % tuple([minimums[a] for a in 'XY'])
    print 'Maximums:', '%s\t%s' % tuple([maximums[a] for a in 'XY'])
    sys.stdout.write('\nTransforming Coordinates\n')
    sys.stdout.flush()
    for command in commands:
        if 'layer' in command:
            sys.stdout.write('.')
            sys.stdout.flush()
        for axis in 'XY':
            if axis in command:
                if 'X' == axis:
                    command[axis] = (command[axis] - 
                            minimums[axis]) * scale + offset[axis]
                else:
                    command[axis] = (maximums[axis] - 
                            command[axis]) * scale + offset[axis]

def preprocessCommands(commands):
    '''Add relative information to each command for use in drawing svgs'''
    oldCommand = dict()
    currentCommand = dict()
    sys.stdout.write('\nParsing Command Transitions\n')
    sys.stdout.flush()
    for command in commands:
        if 'layer' in command:
            sys.stdout.write('.')
            sys.stdout.flush()
        elif 'G1' in command:
            currentCommand.update(command)
            currentCommand['old'] = copy.deepcopy(oldCommand)
            oldCommand.update(currentCommand)
            command.update(currentCommand)
            del oldCommand['old']
            #print encodeCommand(command)

def postprocessCommands(commands):
    '''Convert preprocessed commands into a json-ready dict'''
    layers = []
    movements = []
    
    for command in commands:
        if 'layer' in command:
            if len(movements) > 0:
                layers.append(movements)
            movements = []
        elif 'G1' in command:
            try:
                movement = dict({'type': 'movement'})
                oldPos = dict()
                newPos = dict()
                oldPos['x'] = command['old']['X']
                oldPos['y'] = command['old']['Y']
                newPos['x'] = command['X']
                newPos['y'] = command['Y']
                movement['from'] = oldPos
                movement['to'] = newPos
                movement['speed'] = command['F']
                movement['relative'] = dict()
                for axis in 'xy':
                    movement['relative'][axis] = movement['to'][axis] - movement['from'][axis]
                movement['distance'] = math.sqrt(movement['relative']['x']**2 + movement['relative']['y']**2)
                for tool in 'ABE':
                    if tool in command:
                        movement['volume'] = command[tool] - command['old'][tool]
                        break
                movements.append(movement)
            except KeyError as ke:
                pass
    outDict = dict()
    outDict['layers'] = []
    for layer in layers:
        curLayer = dict({'movements' : layer})
        outDict['layers'].append(curLayer)
    return outDict
    

def parseArgs(argv):
    parser=argparse.ArgumentParser(
        description="Generate customizable analysis of GCode in svg form.")
    #MONKEY PATCH BEGIN
    def argparse_error_override(message):
        parser.print_help()
        parser.exit(2)
    parser.error=argparse_error_override
    #MONKEY PATCH END
    parser.add_argument(
        'GCODE_PATH',
        help='path of gcode to analyze')
    parser.add_argument(
        'OUTPUT_PATH',
        type=os.path.abspath, 
        nargs='?',
        help='top folder where to place generated files',
        default=None)
    return parser.parse_args(argv)

def commandToSvg(command):
    '''Convert a single processed movement to an svg line'''
    if 'G1' in command and 'old' in command:
        #work on a preprocessed command
        relative = dict()
        for param in paramcodes:
            if param in command and param in command['old']:
                relative[param] = command[param] - command['old'][param]
        lineparams = dict()
        try:
            lineparams['x1'] = command['old']['X']
            lineparams['y1'] = command['old']['Y']
            lineparams['x2'] = command['X']
            lineparams['y2'] = command['Y']
            lineparams['style'] = interpretCommand(command)
            return '<%s />' % (formatParamDict(lineparams, 'line'), )
        except KeyError as ke:
            pass
    elif 'type' in command and command['type'] == 'movement':
        #work on a postprocessed command
        try:
            if command ['distance'] > 0:
                #line
                lineparams = dict({
                        'x1': command['from']['x'],
                        'y1': command['from']['y'],
                        'x2': command['to']['x'],
                        'y2': command['to']['y'],
                        'style': interpretCommand(command)
                        })
                return '<%s />' % (formatParamDict(lineparams, 'line'), )
            else:
                #reversal?
                if command['volume'] < 0:
                    #reverse
                    color = 'blue'
                elif command['volume'] > 0:
                    #restart
                    color = 'red'
                else:
                    color = 'rgb(0,255,0)'
                roundparams = dict({
                        'cx': command['to']['x'],
                        'cy': command['to']['y'],
                        'r': 4.0, 
                        'stroke': 'none', 
                        'fill': color
                        })
                return '<%s />' % (formatParamDict(roundparams, 'circle'), )
        except KeyError as ke:
            pass
    return None
    
def monolithicPre(commands, out_dir):
    '''
        Cause svg files to appear in out_dir/svg.
        
        Return a list of file names written
    '''
    layer_num = 0
    layer_name = None
    oldCommands = []
    outFiles = []
    sys.stdout.write('\nRendering SVG files\n')
    sys.stdout.flush()
    for command in commands:
        if 'layer' in command:
            sys.stdout.write('.')
            sys.stdout.flush()
            if None is not layer_name:
                ofilename = os.path.join(out_dir, 'svg', 'layer_%s.svg' % (layer_num))
                with open(ofilename, 'w') as ofile:
                    writeSvg(ofile, [commandToSvg(c) for c in oldCommands])
                outFiles.append(ofilename)
            layer_name = command['layer']
            layer_num += 1
            oldCommands = []
        else:
            oldCommands.append(command)
    return outFiles
 
def monolithicPost(commands, out_dir):
    layer_num = 0
    outFiles = []
    sys.stdout.write('\nRendering SVG files\n')
    sys.stdout.flush()
    for layer in commands['layers']:
        sys.stdout.write('.')
        sys.stdout.flush()
        ofilename = os.path.join(out_dir, 'svg', 'layer_%s.svg' % (layer_num))
        outFiles.append(ofilename)
        with open(ofilename, 'w') as ofile:
            lines = [commandToSvg(c) for c in layer['movements']]
            #circles = ['<%s />' % formatParamDict(c, 'circle')
            #        for c in computeCurvature(layer['movements'])]

            writeSvg(ofile, lines)
        layer_num += 1
    return outFiles
            
    
def monolithicFunc(commands, out_dir):
    if isinstance(commands, dict) and 'layers' in commands:
        return monolithicPost(commands, out_dir)
    else:
        return monolithicPre(commands, out_dir)

def renderIndex(listOfFiles, infile, output):
    output.write('<html><head><title>%s</title></head><body>\n' % (infile))
    output.write('<table>\n')
    for file in listOfFiles:
        output.write('\t<tr>\n')
        output.write('\t\t<td>\n')
        output.write('\t\t\t<a href=\"%s\">%s</a>\n' % (file, os.path.basename(file)))
        output.write('\t\t</td>\n')
        output.write('\t</tr>\n')
    output.write('</table>\n')
    output.write('</body></html>')

def main(argv = None):
    if None is argv:
        argv = sys.argv
    args = parseArgs(argv[1:])
    if None is args.OUTPUT_PATH:
        args.OUTPUT_PATH = os.path.dirname(args.GCODE_PATH)
    OUTPUT_SVG = os.path.join(args.OUTPUT_PATH, 'svg')
    if not os.path.exists(OUTPUT_SVG):
        os.makedirs(OUTPUT_SVG)
    commands = parseCommands(open(args.GCODE_PATH, 'r'))
    commands = dropInitCommands(commands)
    offsetCommands(commands, (32.0,32.0), 10)
    preprocessCommands(commands)
    commandsDict = postprocessCommands(commands)
    outFiles = monolithicFunc(commandsDict, args.OUTPUT_PATH)
    with open(os.path.join(args.OUTPUT_PATH, 'index.html'), 'w') as outIndex:
        renderIndex(outFiles, os.path.basename(args.GCODE_PATH), outIndex)
    

if __name__ == '__main__':
    main()