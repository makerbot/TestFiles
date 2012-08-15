# vim:ai:et:ff=unix:fileencoding=utf-8:sw=4:ts=4:
# conveyor/src/main/python/conveyor/toolpath/skeinforge.py
#
# conveyor - Printing dispatch engine for 3D objects and their friends.
# Copyright © 2012 Matthew W. Samsonoff <matthew.samsonoff@makerbot.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, print_function, unicode_literals)

from decimal import *

import logging
import os
import os.path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback

class SkeinforgeSupport(object):
    def __init__(self):
        self.NONE = 'NONE'
        self.EXTERIOR = 'EXTERIOR'
        self.FULL = 'FULL'

class SkeinforgeConfiguration(object):
    def __init__(self):
        self.skeinforgepath = None
        self.profile = None
        self.raft = False
        self.support = SkeinforgeSupport().NONE
        self.bookend = True
        self.infillratio = Decimal('0.1')
        self.feedrate = Decimal('40')
        self.travelrate = Decimal('55')
        self.filamentdiameter = Decimal('1.82')
        self.pathwidth = Decimal('0.4')
        self.layerheight = Decimal('0.27')
        self.shells = 1

class SkeinforgeToolpath(object):
    def __init__(self, configuration):
        self._configuration = configuration
        self._log = logging.getLogger(self.__class__.__name__)

    def generate(self, stlpath, gcodepath, with_start_end, printer):
        self._log.info('slicing with Skeinforge')
        try:
            directory = os.path.abspath(os.path.dirname(gcodepath))
            try:
                (root, ext) = os.path.splitext(stlpath)
                tmp_stlpath = os.path.join(
                    directory, os.path.basename(root+ext))
                tmp_stldir = os.path.dirname(tmp_stlpath)
                if not os.path.exists(tmp_stldir):
                    os.makedirs(tmp_stldir)
                with open(tmp_stlpath, 'w') as tmp_stlfh, open(stlpath, 'r') as stlfh:
                    stldata = stlfh.read()
                    tmp_stlfh.write(stldata)
                arguments = list(
                    self._getarguments(tmp_stlpath))
                self._log.debug('arguments=%r', arguments)
                subprocess.check_call(arguments)
                tmp_gcodepath = self._gcodepath(tmp_stlpath)
                self._postprocess(gcodepath, tmp_gcodepath, with_start_end, printer)
            finally:
                pass
                os.unlink(tmp_stlpath)
        except Exception as e:
            self._log.exception('unhandled exception')
        else:
            return 0

    def _gcodepath(self, path):
        root, ext = os.path.splitext(path)
        gcode = ''.join((root, '.gcode'))
        return gcode

    def _postprocess(self, gcodepath, tmp_gcodepath, with_start_end, printer):
        return
        gcodelines = []
        with open(tmp_gcodepath, 'r') as fpt:
            gcodelines = fpt.readlines();
        os.unlink(tmp_gcodepath)
        with open(gcodepath, 'w') as fp:
            if with_start_end:
                for line in printer._startlines(): # TODO: replace this hack
                    print(line, file=fp)
            for gcode in gcodelines:
                print(gcode, file=fp)
            if with_start_end:
                for line in printer._endlines():
                    print(line, file=fp)
                
        with open(gcodepath, 'w') as fp:
            if with_start_end:
                for line in printer._startlines(): # TODO: replace this hack
                    print(line, file=fp)
            self._appendgcode(fp, tmp_gcodepath)
            if with_start_end:
                for line in printer._endlines():
                    print(line, file=fp)

    def _appendgcode(self, wfp, path):
        with open(path, 'r') as rfp:
            for line in rfp:
                wfp.write(line)

    def _option(self, module, preference, value):
        yield '--option'
        yield ''.join((module, ':', preference, '=', unicode(value)))

    def _getarguments(self, stlpath):
        for method in (
            self._getarguments_executable,
            self._getarguments_python,
            self._getarguments_skeinforge,
            ):
                for iterable in method(stlpath):
                    for value in iterable:
                        yield value

    def _getarguments_executable(self, stlpath):
        yield (sys.executable,)

    def _getarguments_python(self, stlpath):
        yield ('-u',)
        yield (self._configuration.skeinforgepath,)

    def _getarguments_skeinforge(self, stlpath):
        yield ('-p', self._configuration.profile,)
        for method in (
            self._getarguments_raft,
            self._getarguments_support,
            self._getarguments_bookend,
            self._getarguments_printomatic,
            self._getarguments_stl,
            ):
                for iterable in method(stlpath):
                    yield iterable

    def _getarguments_raft(self, stlpath):
        yield self._option(
            'raft.csv', 'Add Raft, Elevate Nozzle, Orbit:', self._configuration.raft)

    def _getarguments_support(self, stlpath):
        if SkeinforgeSupport().NONE == self._configuration.support:
            yield self._option('raft.csv', 'None', 'true')
            yield self._option('raft.csv', 'Empty Layers Only', 'false')
            yield self._option('raft.csv', 'Everywhere', 'false')
            yield self._option('raft.csv', 'Exterior Only', 'false')
        elif SkeinforgeSupport().EXTERIOR == self._configuration.support:
            yield self._option('raft.csv', 'None', 'false')
            yield self._option('raft.csv', 'Empty Layers Only', 'false')
            yield self._option('raft.csv', 'Everywhere', 'false')
            yield self._option('raft.csv', 'Exterior Only', 'true')
        elif SkeinforgeSupport().FULL == self._configuration.support:
            yield self._option('raft.csv', 'None', 'false')
            yield self._option('raft.csv', 'Empty Layers Only', 'false')
            yield self._option('raft.csv', 'Everywhere', 'true')
            yield self._option('raft.csv', 'Exterior Only', 'false')
        else:
            raise ValueError(self._configuration.support)

    def _getarguments_bookend(self, stlpath):
        if self._configuration.bookend:
            yield self._option('alteration.csv', 'Name of Start File:', '')
            yield self._option('alteration.csv', 'Name of End File:', '')

    def _getarguments_printomatic(self, stlpath):
        yield self._option(
            'fill.csv', 'Infill Solidity (ratio):', self._configuration.infillratio)
        yield self._option(
            'speed.csv', 'Feed Rate (mm/s):', self._configuration.feedrate)
        yield self._option(
            'speed.csv', 'Travel Feed Rate (mm/s):', self._configuration.travelrate)
        yield self._option(
            'speed.csv', 'Flow Rate Setting (float):', self._configuration.feedrate)
        yield self._option(
            'dimension.csv', 'Filament Diameter (mm):',
            self._configuration.filamentdiameter)
        ratio = self._configuration.pathwidth / self._configuration.layerheight
        yield self._option(
            'carve.csv', 'Perimeter Width over Thickness (ratio):', ratio)
        yield self._option(
            'fill.csv', 'Infill Width over Thickness (ratio):', ratio)
        yield self._option(
            'carve.csv', 'Layer Thickness (mm):', self._configuration.layerheight)
        yield self._option(
            'fill.csv', 'Extra Shells on Alternating Solid Layer (layers):',
            self._configuration.shells)
        yield self._option(
            'fill.csv', 'Extra Shells on Base (layers):', self._configuration.shells)
        yield self._option(
            'fill.csv', 'Extra Shells on Sparse Layer (layers):',
            self._configuration.shells)

    def _getarguments_stl(self, stlpath):
        yield (stlpath,)

def slice(argv):
    code = None
    if 5 != len(argv):
        print('usage: %s SKEINFORGE.py PROFILEDIR STL GCODE' % (argv[0],), file=sys.stderr)
        code = 1
    else:
        logging.basicConfig()
        try:
            configuration = SkeinforgeConfiguration()
            configuration.skeinforgepath = os.path.abspath(
                                           os.path.normpath(argv[1]))
            configuration.profile = os.path.abspath(
                                    os.path.normpath(argv[2]))
            
            print(configuration.skeinforgepath)
            print(configuration.profile)
            generator = SkeinforgeToolpath(configuration)
            code = generator.generate(argv[3], argv[4], False, None)
        finally:
            pass
    return code

def main(argv=None):
    if argv is None:
        argv = sys.argv
    slice(argv)

if '__main__' == __name__:
    code = main(sys.argv)
    if None is code:
        code = 0
    sys.exit(code)
