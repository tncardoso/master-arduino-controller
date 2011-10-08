#!/usr/bin/env python

# The following license does not apply to controller.png
#
# Copyright (c) 2011, Thiago C. (tncardoso.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of Thiago C. nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Thiago C. BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE. 

from __future__ import division
import sys
import threading
import pygame
import serial
import ctypes
from datetime import datetime, timedelta

class Dummy:
    '''Dummy for testing without using serial communication'''
    def write(self, txt):
        pass

class MasterController:
    '''Handle serial communication with arduino'''
    def __init__(self):
        self._serial = serial.Serial('/dev/ttyACM0', 9600)
        #self._serial = Dummy()

    # functions programed in the arduino side
    # one byte is written to the serial port. The interpretation
    # of this byte is coded in the arduino side (loop function).
    def pushButtonLeft(self): self._serial.write(chr(1))
    def releaseButtonLeft(self): self._serial.write(chr(2))
    def pushButtonRight(self): self._serial.write(chr(3))
    def releaseButtonRight(self): self._serial.write(chr(4))
    def pushButtonDown(self): self._serial.write(chr(5))
    def releaseButtonDown(self): self._serial.write(chr(6))
    def pushButtonUp(self): self._serial.write(chr(7))
    def releaseButtonUp(self): self._serial.write(chr(8))
    def pushButtonA(self): self._serial.write(chr(9))
    def releaseButtonA(self): self._serial.write(chr(10))
    def pushButtonB(self): self._serial.write(chr(11))
    def releaseButtonB(self): self._serial.write(chr(12))

class DrawThread(threading.Thread):
    '''Thread for drawing the canvas. This task is done in a separate
    thread in order to process events with little delay'''
    def __init__ (self, gui):
        threading.Thread.__init__(self)
        self._gui = gui

    def run(self):
        clock = pygame.time.Clock()
        while not self._gui._finished:
            self._gui._screen.blit(self._gui._controller, self._gui._controller.get_rect())
            self.drawButtonA()
            self.drawButtonB()
            self.drawButtonUp()
            self.drawButtonDown()
            self.drawButtonLeft()
            self.drawButtonRight()
            pygame.display.flip()
            clock.tick(30)
    
    # functions for rendering pressed keys
    def drawButtonA(self):
        if self._gui._button_a:
            pygame.draw.circle(self._gui._screen, pygame.Color('red'), (271,149), 20, 6)
    def drawButtonB(self):
        if self._gui._button_b:
            pygame.draw.circle(self._gui._screen, pygame.Color('red'), (331,149), 20, 6)
    def drawButtonUp(self):
        if self._gui._button_up:
            pygame.draw.rect(self._gui._screen, pygame.Color('red'), pygame.Rect((110,95,8,16)))
    def drawButtonDown(self):
        if self._gui._button_down:
            pygame.draw.rect(self._gui._screen, pygame.Color('red'), pygame.Rect((110,153,8,16)))
    def drawButtonLeft(self):
        if self._gui._button_left:
            pygame.draw.rect(self._gui._screen, pygame.Color('red'), pygame.Rect((77,127,16,8)))
    def drawButtonRight(self):
        if self._gui._button_right:
            pygame.draw.rect(self._gui._screen, pygame.Color('red'), pygame.Rect((135,127,16,8)))

class Gui:
    '''Graphical interface used to control the arduino'''
    def __init__(self, replay=None, record=None):
        # init pygame lib
        pygame.init()

        # check if events should be recorded
        if record is None: self._record = None
        else: self._record = open(record, 'w')

        # check if events should be replayed
        if replay is None: self._replay = None
        else: self._replay = open(replay, 'r')
        
        self._atime = datetime.now()

        # set window size and get screen
        self._width = 400
        self._height = 270
        self._screen = pygame.display.set_mode((self._width, self._height))
        self._finished = False

        # load resources
        self._controller = ball = pygame.image.load('controller.png')

        # start serial connection
        self._serial = MasterController()

        # drawing thread
        self._dthread = DrawThread(self)

        # set controller state
        self._button_a = False
        self._button_b = False
        self._button_up = False
        self._button_down = False
        self._button_left = False
        self._button_right = False

        # actions
        # maps event to key to action: e.g. actions[KEYUP][K_z]
        self._actions = { pygame.KEYDOWN: {}, pygame.KEYUP: {} }
        self._actions[pygame.KEYDOWN][pygame.K_z] =     self.pushButtonA
        self._actions[pygame.KEYUP][pygame.K_z] =       self.releaseButtonA
        self._actions[pygame.KEYDOWN][pygame.K_x] =     self.pushButtonB
        self._actions[pygame.KEYUP][pygame.K_x] =       self.releaseButtonB
        self._actions[pygame.KEYDOWN][pygame.K_UP] =    self.pushButtonUp
        self._actions[pygame.KEYUP][pygame.K_UP] =      self.releaseButtonUp
        self._actions[pygame.KEYDOWN][pygame.K_DOWN] =  self.pushButtonDown
        self._actions[pygame.KEYUP][pygame.K_DOWN] =    self.releaseButtonDown
        self._actions[pygame.KEYDOWN][pygame.K_LEFT] =  self.pushButtonLeft
        self._actions[pygame.KEYUP][pygame.K_LEFT] =    self.releaseButtonLeft
        self._actions[pygame.KEYDOWN][pygame.K_RIGHT] = self.pushButtonRight
        self._actions[pygame.KEYUP][pygame.K_RIGHT] =   self.releaseButtonRight

        # force arduino release
        for key, func in self._actions[pygame.KEYUP].iteritems():
            func()

    def __del__(self):
        self._record.close()

    def run(self):
        self._dthread.start()

        # last action time
        self._atime = datetime.now()

        # check if it is a playback
        if self._replay is not None:
            self.replay()

        while not self._finished:
            # only process events in the main thread
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._finished = True
                    return
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.checkKeyEvent(event.type, event.key)
            pygame.time.wait(10)

    def replay(self):
        # load all replay data into memory and
        # prepare execution tuples
        print 'loading replay data'
        actions = []
        for action in self._replay.readlines():
            spt = action.split()
            if spt[2] == 'P': action = pygame.KEYDOWN
            else: action = pygame.KEYUP

            if spt[3] == 'A': button = pygame.K_z
            elif spt[3] == 'B': button = pygame.K_x
            elif spt[3] == 'U': button = pygame.K_UP
            elif spt[3] == 'D': button = pygame.K_DOWN
            elif spt[3] == 'L': button = pygame.K_LEFT
            else: button = pygame.K_RIGHT

            sec = int(spt[0])
            nsec = int(spt[1])
            print 'appending action= %s button= %s sec= %s nsec=%s'%(action,
                    button, sec, nsec)
            actions.append((sec, nsec, action, button))

            # check events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._finished = True
                    return

        # execute replay loop
        for sec, nsec, state, button in actions:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._finished = True
                    return
           
            nanosleep(sec, nsec)
            self.checkKeyEvent(state, button)

    def checkKeyEvent(self, state, key):
        # not good to use try/cache for normal behavior
        # but this is faster than using find every time
        try:
            f = self._actions[state][key]
            f()
        except KeyError:
            # key not mapped
            pass

    def total_seconds(self, td):
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

    def recordAction(self, state, button):
        '''Check if action should be recorded'''
        if self._record is not None:
            now = datetime.now()
            td = now - self._atime
            self._atime = now
            self._record.write('%d %s %s %s\n'%(td.seconds,
                td.microseconds * (10**3), state, button))
            
    def pushButtonA(self):
        self._serial.pushButtonA()
        self._button_a = True
        self.recordAction('P','A')
    def releaseButtonA(self):
        self._serial.releaseButtonA()
        self._button_a = False
        self.recordAction('R','A')
    def pushButtonB(self):
        self._serial.pushButtonB()
        self._button_b = True
        self.recordAction('P','B')
    def releaseButtonB(self):
        self._serial.releaseButtonB()
        self._button_b = False
        self.recordAction('R','B')
    def pushButtonUp(self):
        self._serial.pushButtonUp()
        self._button_up = True
        self.recordAction('P','U')
    def releaseButtonUp(self):
        self._serial.releaseButtonUp()
        self._button_up = False
        self.recordAction('R','U')
    def pushButtonDown(self):
        self._serial.pushButtonDown()
        self._button_down = True
        self.recordAction('P','D')
    def releaseButtonDown(self):
        self._serial.releaseButtonDown()
        self._button_down = False
        self.recordAction('R','D')
    def pushButtonLeft(self):
        self._serial.pushButtonLeft()
        self._button_left = True
        self.recordAction('P','L')
    def releaseButtonLeft(self):
        self._serial.releaseButtonLeft()
        self._button_left = False
        self.recordAction('R','L')
    def pushButtonRight(self):
        self._serial.pushButtonRight()
        self._button_right = True
        self.recordAction('P','R')
    def releaseButtonRight(self):
        self._serial.releaseButtonRight()
        self._button_right = False
        self.recordAction('R','R')

# nanosleep function for better time resolution
libc = ctypes.CDLL('libc.so.6')
class timespec(ctypes.Structure):
    # parameters t_time sec and long nsec
    _fields_ = [('sec', ctypes.c_long), ('nsec', ctypes.c_long)]   
libc.nanosleep.argtypes = [ctypes.POINTER(timespec), ctypes.POINTER(timespec)]
  
def nanosleep(sec, nsec):
    req = timespec()
    req.sec = sec
    req.nsec = nsec
    rem = timespec()
    # nanosleep returns -1 in case of interruption and write rem with
    # the remaining time
    while libc.nanosleep(req, rem) == -1:
        req = rem
        rem = timespec()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        gui = Gui()
    else:
        if sys.argv[1] == 'record':
            gui = Gui(record=sys.argv[2])
        elif sys.argv[1] == 'replay':
            gui = Gui(replay=sys.argv[2])
    gui.run()

