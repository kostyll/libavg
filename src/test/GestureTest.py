# -*- coding: utf-8 -*-
# libavg - Media Playback Engine.
# Copyright (C) 2003-2011 Ulrich von Zadow
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Current versions can be found at www.libavg.de
#

from libavg import avg, ui

import math
from sets import Set
from testcase import *

class GestureTestCase(AVGTestCase):
    
    DETECTED = 1
    MOVED = 2
    UP = 3
    ENDED = 4
    POSSIBLE = 5
    FAILED = 6
    
    def __init__(self, testFuncName):
        AVGTestCase.__init__(self, testFuncName)


    def testTapRecognizer(self):

        def onPossible(event):
            self.__possible = True

        def onDetected(event):
            self.__detected = True

        def onFail(event):
            self.__failed = True

        def initState():
            self.__possible = False
            self.__detected = False
            self.__failed = False

        def abort():
            self.__tapRecognizer.abort()
            initState()

        def enable(isEnabled):
            self.__tapRecognizer.enable(isEnabled)
            initState()

        EVENT_POSSIBLE = 1
        EVENT_DETECTED = 2
        EVENT_FAILED = 3
        def assertEvents(flags):
            self.assert_((EVENT_POSSIBLE in flags) == self.__possible)
            self.assert_((EVENT_DETECTED in flags) == self.__detected)
            self.assert_((EVENT_FAILED in flags) == self.__failed)

        root = self.loadEmptyScene()
        image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
        self.__tapRecognizer = ui.TapRecognizer(image,
                possibleHandler=onPossible,
                detectedHandler=onDetected,
                failHandler=onFail)
        initState()
        Player.setFakeFPS(10)
        self.start((
                 # Down-up: recognized as tap.
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 # Down-small move-up: recognized as tap.
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: self._sendMouseEvent(avg.CURSORMOTION, 31, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 # Down-big move-up: fail
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 1, 1),
                 lambda: self._sendMouseEvent(avg.CURSORMOTION, 150, 50),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 1, 1),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 # Down-delay: fail
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: self.delay(1000),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 # Down-Abort-Up: not recognized as tap
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 abort,
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 # Abort-Down-Up: recognized as tap
                 initState,
                 abort,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 # Down-Abort-Up-Down-Up: recognized as tap
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 0, 0),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 abort,
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 # Disable-Down-Up-Enable: not recognized as tap
                 initState,
                 lambda: enable(False),
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: enable(True),
                 # Down-Disable-Up-Enable: not recognized as tap
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: enable(False),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: enable(True),
                 # Down-Disable-Enable-Up: not recognized as tap
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: enable(False),
                 lambda: enable(True),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 # Down-Disable-Up-Enable-Down-Up: recognized as tap
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])), 
                 lambda: enable(False),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: enable(True),
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 # Down-Abort-Disable-Up-Enable: not recognized as tap
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 abort,
                 lambda: enable(False),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: enable(True),
                 # Abort-Disable-Abort-Enable-Abort-Down-Up: recognized as tap
                 initState,
                 abort,
                 lambda: enable(False),
                 abort,
                 lambda: enable(True),
                 abort,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                ))


    def testHoldRecognizer(self):

        def onPossible(event):
            self.__possible = True

        def onDetected(event):
            self.__detected = True

        def onFail(event):
            self.__failed = True

        def onStop(event):
            self.__stopped = True

        def initState():
            self.__possible = False
            self.__detected = False
            self.__failed = False
            self.__stopped = False

        def abort():
            self.__holdRecognizer.abort()
            initState()

        def enable(isEnabled):
            self.__holdRecognizer.enable(isEnabled)
            initState()

        EVENT_POSSIBLE = 1
        EVENT_DETECTED = 2
        EVENT_FAILED = 3
        EVENT_STOPPED = 4
        def assertEvents(flags):
            self.assert_((EVENT_POSSIBLE in flags) == self.__possible)
            self.assert_((EVENT_DETECTED in flags) == self.__detected)
            self.assert_((EVENT_FAILED in flags) == self.__failed)
            self.assert_((EVENT_STOPPED in flags) == self.__stopped)

        Player.setFakeFPS(2)
        root = self.loadEmptyScene()
        image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
        self.__holdRecognizer = ui.HoldRecognizer(image,
                delay=1000,
                possibleHandler=onPossible, 
                detectedHandler=onDetected, 
                failHandler=onFail, 
                stopHandler=onStop)
        initState()
        self.start((
                 # Standard down-hold-up sequence.
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 None,
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 None,
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED,
                         EVENT_STOPPED])),

                 # down-up sequence, hold not long enough.
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),

                 # down-move-up sequence, should stop. 
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 1, 1),
                 lambda: self._sendMouseEvent(avg.CURSORMOTION, 150, 50),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 150, 50),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),

                 # down-hold-abort-up, should not recognized
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 None,
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 None,
                 abort,
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),

                 # down-abort-hold-up, should not recognized
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 abort,
                 None,
                 lambda: assertEvents(Set([])),
                 None,
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),

                 # down-hold-disabled-up-enabled, should not recognized
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 None,
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_DETECTED])),
                 None,
                 lambda: enable(False),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                 lambda: enable(True),

                 # down-disabled-enabled-hold-up, should not recognized
                 initState,
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: assertEvents(Set([EVENT_POSSIBLE])),
                 lambda: enable(False),
                 lambda: enable(True),
                 None,
                 lambda: assertEvents(Set([])),
                 None,
                 lambda: self._sendMouseEvent(avg.CURSORUP, 30, 30),
                 lambda: assertEvents(Set([])),
                ))
        Player.setFakeFPS(-1)


    def testDoubletapRecognizer(self):

        EVENT_POSSIBLE = 1
        EVENT_DETECTED = 2
        EVENT_FAILED = 3
        def onPossible(event):
            self.__flags.add(EVENT_POSSIBLE)

        def onDetected(event):
            self.__flags.add(EVENT_DETECTED)

        def onFail(event):
            self.__flags.add(EVENT_FAILED)

        def initState():
            self.__flags = Set()

        def assertEvents(flags):
            wantedFlags = Set(flags)
            if wantedFlags != self.__flags:
                print "State expected: ", wantedFlags
                print "Actual state: ", self.__flags
                self.assert_(False)

        def checkMouseEvent(type, x, y, eventFlags):
            return [
                     lambda: self._sendMouseEvent(type, x, y),
                     lambda: assertEvents(eventFlags)
                    ]

        def abort():
            self.__tapRecognizer.abort()
            initState()

        def enable(isEnabled):
            self.__tapRecognizer.enable(isEnabled)
            initState()

        root = self.loadEmptyScene()
        image = avg.ImageNode(parent=root, href="rgb24-64x64.png", size=(128,128))
        self.__tapRecognizer = ui.DoubletapRecognizer(image,
                possibleHandler=onPossible,
                detectedHandler=onDetected,
                failHandler=onFail)
        initState()
        Player.setFakeFPS(20)
        self.start((
                 # Down, up, down, up: click
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE, EVENT_DETECTED]),
                 # Down, move: stop
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 0, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORMOTION, 80, 30, 
                        [EVENT_POSSIBLE, EVENT_FAILED]),
                 checkMouseEvent(avg.CURSORUP, 0, 30, [EVENT_POSSIBLE, EVENT_FAILED]),
                 # Down, up, move: stop
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 0, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 0, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORMOTION, 80, 30, [EVENT_POSSIBLE]),
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 80, 30, [EVENT_FAILED]),
                 initState,
                 checkMouseEvent(avg.CURSORUP, 0, 30, []),
                 # Down, up, down, move: stop
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 0, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 0, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 0, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORMOTION, 80, 30, 
                        [EVENT_POSSIBLE, EVENT_FAILED]),
                 checkMouseEvent(avg.CURSORUP, 0, 30, [EVENT_POSSIBLE, EVENT_FAILED]),
                 # Down,delay: stop
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 lambda: self.delay(600),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE, EVENT_FAILED]),
                 # Down, up, delay: stop
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 lambda: self.delay(600),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 # Down, up, down, delay: stop
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 lambda: self.delay(600),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE, EVENT_FAILED]),
                 # Down, abort, up, down, up, delay: just one click
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 abort,
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 lambda: self.delay(600),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 # Down, up, abort, down, up, delay: two clicks but no double-click
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 abort,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 lambda: self.delay(600),
                 lambda: assertEvents(Set([EVENT_POSSIBLE, EVENT_FAILED])),
                 # Down, up, down, abort, up: just one click
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 abort,
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 # Down, abort, up, down, up, down up: first aborted then recognized
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 abort,
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE, EVENT_DETECTED]),
                 # Disabled, down, up, down, up, enabled: nothing
                 initState,
                 lambda: enable(False),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, []),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, []),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 lambda: enable(True),                 
                 # Down, disabled up, down, up, enabled: just one down
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 lambda: enable(False),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, []),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 lambda: enable(True),
                 # Down, up, disabled, down, up, enabled: just one click
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 lambda: enable(False),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, []),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 lambda: enable(True),
                 # Down, up, down, disabled, up, enabled: just one click
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 lambda: enable(False),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 lambda: enable(True),
                 # Down, disabled, enabled, up, down, up: just one click
                 initState,
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 lambda: enable(False),
                 lambda: enable(True),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 # Down, disabled, enabled, up, down, up, down, up: recognized
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 lambda: enable(False),
                 lambda: enable(True),
                 checkMouseEvent(avg.CURSORUP, 30, 30, []),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORDOWN, 30, 30, [EVENT_POSSIBLE]),
                 checkMouseEvent(avg.CURSORUP, 30, 30, [EVENT_POSSIBLE, EVENT_DETECTED]),
                ))


    def testDragRecognizer(self):

        def onDetected(event):
            self.__addEventFlag(GestureTestCase.DETECTED)

        def onMove(event, offset):
            if self.friction == -1:
                self.assertEqual(offset, (40,40))
            self.__addEventFlag(GestureTestCase.MOVED)

        def onUp(event, offset):
            if self.friction == -1:
                self.assertEqual(offset, (10,-10))
            self.__addEventFlag(GestureTestCase.UP)

        def onEnd(event):
            self.__addEventFlag(GestureTestCase.ENDED)

        def enable(isEnabled):
            dragRecognizer.enable(isEnabled)
            self.__resetEventState()

        def abort():
            dragRecognizer.abort()
            self.__resetEventState()

        Player.setFakeFPS(100)
        for self.friction in (-1, 100):
            root = self.loadEmptyScene()
            image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
            dragRecognizer = ui.DragRecognizer(image, 
                    detectedHandler=onDetected, moveHandler=onMove, upHandler=onUp, 
                    endHandler=onEnd, friction=self.friction)
            self.__resetEventState()
            self.start((
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, 
                            [GestureTestCase.DETECTED]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 70, 70, 
                            [GestureTestCase.MOVED]),
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, 
                            [GestureTestCase.UP, GestureTestCase.ENDED]),
                     lambda: enable(False),
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, []),
                     lambda: dragRecognizer.enable(True),
                     self.__checkMouseEvents(avg.CURSORUP, 30, 30, []),
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, 
                            [GestureTestCase.DETECTED]),
                    ))

        # Test with constraint.
        def onPossible(event):
            self.__flags.add(GestureTestCase.POSSIBLE)

        def onFail(event):
            self.__flags.add(GestureTestCase.FAILED)

        def onVertMove(event, offset):
            if self.friction == -1:
                self.assertEqual(offset, (0,40))
            self.__flags.add(GestureTestCase.MOVED)

        for self.friction in (-1, 100):
            root = self.loadEmptyScene()
            image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
            dragRecognizer = ui.DragRecognizer(image, 
                    possibleHandler=onPossible, failHandler=onFail, 
                    detectedHandler=onDetected, 
                    moveHandler=onVertMove, upHandler=onUp, endHandler=onEnd, 
                    friction=self.friction, direction=ui.DragRecognizer.VERTICAL)
            self.__resetEventState()
            self.start((
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, 
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 35, 30, []),
                     self.__checkMouseEvents(avg.CURSORMOTION, 30, 70, 
                            [GestureTestCase.DETECTED, GestureTestCase.MOVED]),
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, 
                            [GestureTestCase.UP, GestureTestCase.ENDED]),
                     # Wrong direction -> stop.
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30,
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 70, 30, 
                            [GestureTestCase.FAILED]),
                     self.__checkMouseEvents(avg.CURSORUP, 70, 30, []),

                     # No movement -> stop.
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30,
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORUP, 30, 30, 
                            [GestureTestCase.FAILED]),

                     # Down, Abort, Motion, Motion, Up -> not recognized
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30,
                            [GestureTestCase.POSSIBLE]),
                     abort,
                     self.__checkMouseEvents(avg.CURSORMOTION, 35, 30, []),
                     self.__checkMouseEvents(avg.CURSORMOTION, 30, 70, []),
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, []),

                     # Down, Motion, Abort, Motion, Up -> not Recognized
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30,
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 35, 30, []),
                     abort,
                     self.__checkMouseEvents(avg.CURSORMOTION, 30, 70, []),
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, []),

                     # Down, Motion, Motion, Abort, Up -> not recognized
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, 
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 35, 30, []),
                     self.__checkMouseEvents(avg.CURSORMOTION, 30, 70,
                            [GestureTestCase.DETECTED, GestureTestCase.MOVED]),
                     abort,
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, []),

                     # Down, Motion, Abort, Up, Down, Motion, Motion, Up -> Recognized
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30,
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 35, 30, []),
                     abort,
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, []),
                     
                     self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, 
                            [GestureTestCase.POSSIBLE]),
                     self.__checkMouseEvents(avg.CURSORMOTION, 35, 30, []),
                     self.__checkMouseEvents(avg.CURSORMOTION, 30, 70,
                            [GestureTestCase.DETECTED, GestureTestCase.MOVED]),
                     self.__checkMouseEvents(avg.CURSORUP, 40, 20, 
                            [GestureTestCase.UP, GestureTestCase.ENDED]),
                    ))

        # Test second down during inertia.
        root = self.loadEmptyScene()
        image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
        dragRecognizer = ui.DragRecognizer(image, 
                possibleHandler=onPossible, failHandler=onFail, 
                detectedHandler=onDetected, 
                moveHandler=onMove, upHandler=onUp, endHandler=onEnd, 
                friction=0.01)
        self.__resetEventState()
        self.start((
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: self._sendMouseEvent(avg.CURSORUP, 40, 20),
                 self.__resetEventState,
                 self.__checkMouseEvents(avg.CURSORDOWN, 40, 20, 
                            [GestureTestCase.ENDED, GestureTestCase.DETECTED, 
                             GestureTestCase.MOVED]),
                 ))

        # Test second down during inertia, constrained recognizer
        root = self.loadEmptyScene()
        image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
        dragRecognizer = ui.DragRecognizer(image, 
                possibleHandler=onPossible, failHandler=onFail, 
                detectedHandler=onDetected, 
                moveHandler=onMove, upHandler=onUp, endHandler=onEnd, 
                friction=0.01, direction=ui.DragRecognizer.VERTICAL)
        self.__resetEventState()
        self.start((
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 self.__checkMouseEvents(avg.CURSORMOTION, 30, 70,
                        [GestureTestCase.DETECTED, GestureTestCase.MOVED, 
                         GestureTestCase.POSSIBLE]),
                 self.__checkMouseEvents(avg.CURSORUP, 30, 70,
                        [GestureTestCase.MOVED, GestureTestCase.UP]),
                 self.__checkMouseEvents(avg.CURSORDOWN, 30, 30, 
                        [GestureTestCase.MOVED, GestureTestCase.ENDED, 
                         GestureTestCase.POSSIBLE]),
                 self.__checkMouseEvents(avg.CURSORMOTION, 30, 70, 
                        [GestureTestCase.DETECTED, GestureTestCase.MOVED]),
                 ))

        Player.setFakeFPS(-1)


    def testDragRecognizerRelCoords(self):

        def onDrag(event, offset):
            self.assertAlmostEqual(offset, (-40,-40))

        Player.setFakeFPS(100)
        for self.friction in (-1, 100):
            root = self.loadEmptyScene()
            div = avg.DivNode(pos=(64,64), angle=math.pi, parent=root)
            image = avg.ImageNode(parent=div, href="rgb24-64x64.png")
            ui.DragRecognizer(image, moveHandler=onDrag, friction=self.friction)
            self.start((
                     lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                     lambda: self._sendMouseEvent(avg.CURSORMOTION, 70, 70),
                    ))
        Player.setFakeFPS(-1)


    def testDragRecognizerInitialEvent(self):

        def onMotion(event):
            ui.DragRecognizer(self.image, 
                    detectedHandler=onDragStart, moveHandler=onDrag, initialEvent=event)
            self.image.disconnectEventHandler(self)

        def onDragStart(event):
            self.__dragStartCalled = True

        def onDrag(event, offset):
            self.assertEqual(offset, (10,0))

        root = self.loadEmptyScene()
        self.image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
        self.image.connectEventHandler(avg.CURSORMOTION, avg.MOUSE, self, onMotion)
        self.__dragStartCalled = False
        self.start((
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: self._sendMouseEvent(avg.CURSORMOTION, 40, 30),
                 lambda: self._sendMouseEvent(avg.CURSORMOTION, 50, 30),
                ))
        assert(self.__dragStartCalled)


    def testDragRecognizerCoordSysNode(self):

        def onDrag(event, offset):
            self.assertEqual(offset, (40,40))

        root = self.loadEmptyScene()
        div = avg.DivNode(pos=(64,64), angle=math.pi, parent=root)
        image = avg.ImageNode(parent=div, href="rgb24-64x64.png")
        ui.DragRecognizer(image, moveHandler=onDrag, coordSysNode=div, friction=-1)
        self.start((
                 lambda: self._sendMouseEvent(avg.CURSORDOWN, 30, 30),
                 lambda: self._sendMouseEvent(avg.CURSORMOTION, 70, 70),
                ))


    def testTransformRecognizer(self):

        def onDetected(event):
            pass

        def onMove(transform):
            self.transform = transform

        def onUp(transform):
            self.transform = transform

        def checkTransform(expectedTransform):
#            print self.transform
#            print expectedTransform
#            print
            self.assertAlmostEqual(self.transform.trans, expectedTransform.trans)
            self.assertAlmostEqual(self.transform.rot, expectedTransform.rot)
            self.assertAlmostEqual(self.transform.scale, expectedTransform.scale)
            if expectedTransform.rot != 0 or expectedTransform.scale != 1:
                self.assertAlmostEqual(self.transform.pivot, expectedTransform.pivot)

        def createTransTestFrames():
            return (
                    lambda: self._sendTouchEvent(1, avg.CURSORDOWN, 10, 10),
                    lambda: self._sendTouchEvent(1, avg.CURSORUP, 20, 10),
                    lambda: checkTransform(ui.Transform((10,0))),
                )

        def createRotTestFrames(expectedTransform):
            return (
                    lambda: self._sendTouchEvents((
                            (1, avg.CURSORDOWN, 0, 10),
                            (2, avg.CURSORDOWN, 0, 20))),
                    lambda: self._sendTouchEvents((
                            (1, avg.CURSORMOTION, 0, 20),
                            (2, avg.CURSORMOTION, 0, 10))),
                    lambda: checkTransform(expectedTransform),
                    lambda: self._sendTouchEvents((
                            (1, avg.CURSORUP, 0, 20),
                            (2, avg.CURSORUP, 0, 10))),
                )

        def createScaleTestFrames(expectedTransform):
            return (
                 lambda: self._sendTouchEvent(1, avg.CURSORDOWN, 0, 10),
                 lambda: self._sendTouchEvent(2, avg.CURSORDOWN, 0, 20),
                 lambda: self._sendTouchEvent(1, avg.CURSORMOTION, 0, 10),
                 lambda: self._sendTouchEvent(2, avg.CURSORMOTION, 0, 30),
                 lambda: checkTransform(expectedTransform),
                 lambda: self._sendTouchEvent(1, avg.CURSORUP, 0, 10),
                 lambda: self._sendTouchEvent(2, avg.CURSORUP, 0, 30),
                )

        root = self.loadEmptyScene()
        image = avg.ImageNode(parent=root, href="rgb24-64x64.png")
        self.__transformRecognizer = ui.TransformRecognizer(image, 
                detectedHandler=onDetected, moveHandler=onMove, upHandler=onUp)
        self.start((
                 # Check up/down handling
                 lambda: self._sendTouchEvent(1, avg.CURSORDOWN, 10, 10),
                 lambda: checkTransform(ui.Transform((0,0))),
                 lambda: self._sendTouchEvent(1, avg.CURSORMOTION, 20, 10),
                 lambda: checkTransform(ui.Transform((10,0))),
                 lambda: self._sendTouchEvent(2, avg.CURSORDOWN, 20, 20),
                 lambda: checkTransform(ui.Transform((0,0))),
                 lambda: self._sendTouchEvents((
                        (1, avg.CURSORMOTION, 30, 10),
                        (2, avg.CURSORMOTION, 30, 20))),
                 lambda: checkTransform(ui.Transform((10,0))),
                 lambda: self._sendTouchEvent(2, avg.CURSORUP, 30, 20),
                 lambda: checkTransform(ui.Transform((0,0))),
                 lambda: self._sendTouchEvent(1, avg.CURSORMOTION, 40, 10),
                 lambda: checkTransform(ui.Transform((10,0))),
                 lambda: self._sendTouchEvent(1, avg.CURSORUP, 50, 10),
                 lambda: checkTransform(ui.Transform((10,0))),

                 createRotTestFrames(ui.Transform((0,0), math.pi, 1, (0,15))),

                 createScaleTestFrames(ui.Transform((0,5), 0, 2, (0,20)))
                ))

        # Test rel. coords.
        root = self.loadEmptyScene()
        div = avg.DivNode(parent=root, pos=(0,10))
        image = avg.ImageNode(parent=div, href="rgb24-64x64.png")
        self.__transformRecognizer = ui.TransformRecognizer(image, 
                detectedHandler=onDetected, moveHandler=onMove, upHandler=onUp)
        self.start((
            createTransTestFrames(),
            createRotTestFrames(ui.Transform((0,0), math.pi, 1, (0,5))),
            createScaleTestFrames(ui.Transform((0,5), 0, 2, (0,10))),
            ))

        # Test coordSysNode.
        root = self.loadEmptyScene()
        div = avg.DivNode(parent=root, pos=(0,10))
        image = avg.ImageNode(parent=div, href="rgb24-64x64.png")
        self.__transformRecognizer = ui.TransformRecognizer(image, coordSysNode=div,
                detectedHandler=onDetected, moveHandler=onMove, upHandler=onUp)
        self.start((
            createTransTestFrames(),
            createRotTestFrames(ui.Transform((0,0), math.pi, 1, (0,15))),
            createScaleTestFrames(ui.Transform((0,5), 0, 2, (0,20))),
            ))

        root = self.loadEmptyScene()
        div = avg.DivNode(parent=root, pos=(0,10))
        image = avg.ImageNode(parent=div, href="rgb24-64x64.png")
        self.__transformRecognizer = ui.TransformRecognizer(image, friction=0.01,
                detectedHandler=onDetected, moveHandler=onMove, upHandler=onUp)
        self.start((
                lambda: self._sendTouchEvent(1, avg.CURSORDOWN, 10, 10),
                lambda: self._sendTouchEvent(1, avg.CURSORUP, 20, 10),
                lambda: self._sendTouchEvent(1, avg.CURSORDOWN, 10, 10),
                lambda: self._sendTouchEvent(1, avg.CURSORUP, 20, 10),
               ))  


    def testKMeans(self):
        pts = [avg.Point2D(0,0), avg.Point2D(0,1)]
        means = ui.calcKMeans(pts)
        self.assertEqual(means, ([0], [1]))

        pts.append (avg.Point2D(0,4))
        means = ui.calcKMeans(pts)
        self.assertEqual(means, ([0,1], [2]))


    def testMat3x3(self):
        t = ui.Mat3x3.translate([1,0,1])
        v = [1,0,1]
        self.assertEqual(t.applyVec(v), [2,0,1])
        r = ui.Mat3x3.rotate(math.pi/2)
        self.assertAlmostEqual(r.applyVec(v), [0,1,1])
        t2 = t.applyMat(t)
        self.assertAlmostEqual(t.applyMat(t).m, ui.Mat3x3.translate([2,0,1]).m)
        self.assertAlmostEqual(t.applyMat(r).m, ui.Mat3x3([0,-1,1],[1,0,0]).m)
        self.assertAlmostEqual(r.applyMat(t).m, ui.Mat3x3([0,-1,0],[1,0,1]).m)
        self.assertAlmostEqual(ui.Mat3x3().m, ui.Mat3x3().inverse().m)
        m = ui.Mat3x3([-1,  3, -3], 
                      [ 0, -6,  5],
                      [-5, -3,  1])
        im = ui.Mat3x3([3./2,      1., -1./2],
                       [-25./6, -8./3,  5./6],
                       [-5.,      -3.,    1.])
        self.assertAlmostEqual(m.inverse().m, im.m)

        image = avg.ImageNode(pos=(10,20), size=(30,40), angle=1.57, 
            href="rgb24alpha-64x64.png")
        mat = ui.Mat3x3.fromNode(image)
        mat.setNodeTransform(image)
        self.assertAlmostEqual(image.pos, (10,20))
        self.assertAlmostEqual(image.size, (30,40))
        self.assertAlmostEqual(image.angle, 1.57)

    def __checkMouseEvents(self, type, x, y, expectedEvents):
        return [
                 lambda: self._sendMouseEvent(type, x, y),
                 lambda: self.__assertEvents(expectedEvents),
                 self.__resetEventState
                ]
    
    def __assertEvents(self, expectedFlags):
        expectedFlags = Set(expectedFlags)
        if expectedFlags != self.__flags:
            print "State expected: ", expectedFlags
            print "Actual state: ", self.__flags
            self.assert_(False)

    def __resetEventState(self):
        self.__flags = Set()

    def __addEventFlag(self, flag):
        self.__flags.add(flag)


def gestureTestSuite(tests):
    availableTests = (
        "testTapRecognizer",
        "testHoldRecognizer",
        "testDoubletapRecognizer",
        "testDragRecognizer",
        "testDragRecognizerRelCoords",
        "testDragRecognizerInitialEvent",
        "testDragRecognizerCoordSysNode",
        "testTransformRecognizer",
        "testKMeans",
        "testMat3x3",
        )

    return createAVGTestSuite(availableTests, GestureTestCase, tests)

Player = avg.Player.get()
