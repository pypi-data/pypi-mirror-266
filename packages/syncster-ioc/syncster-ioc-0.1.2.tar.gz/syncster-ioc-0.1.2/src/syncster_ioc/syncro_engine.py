#!/usr/bin/python3

#
#        Syncster Library for terminal access to Menlo Syncro synchronizers.
#        Copyright (C) 2022 Florin Boariu.
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import struct
import serial
import asyncio
import time

from syncster import rbp, hrt

import traceback

import logging
logger = logging.getLogger(__name__)

''' Synchro driver application.

Implements a state machine to put, hold and handle the Menlo Sychro in
a well-defined "sychronized state", and deal with events related to that
(loss of synchronization etc).

FIXME: need to decide whether to drag the Menlo DDS-120, which is actually
       a different device sometimes connected through a different interface,
       into this

Simple state machine (expand as needed):

                     START
                       ┊
                       ▼
              ┌┄┄┄┄┄┄┄INIT┄┄┄┄►┄┄┄┐
              ┊        ┊          ┊
              ┊        ┊          ┊
              ┊        ┊          ┊
              ┊        ▼          ┊
              ├┄┄◄┄┄┄SYNCED┄┄┄►┄┄┄┤
              ┊        ▲          ┊
              ┊        ┊          ┊
              ▼        ┊          ┊
        ┌┄┄┄►OFF┄┄►┄┄STRAY┄┄┄┄►┄┄┄┤
        ┊     ┊                   ┊
        ┊     ┊                   ┊
        ┊     ▼                   ┊
        └┄┄┄ERROR◄┄┄┄┄┄┄┄┄┄┄┄┄◄┄┄┄┘

  

The states have the following meaning:

  - START: starting state on software startup (unknown state of the Synchro
    hardare)

  - INIT: initial state determination -- tries to retain hardware state,
    if tracking was OFF or SYNCED previously.

  - OFF: tracking / synchronization not active; waiting for user input to
    activate.

  - STRAY: trying to synchronize, or wait for external synchronization attempt
    (e.g. by manual user intevention at the Syncro Box's UI panel)

  - SYNCED: synchronization / tracking active, system ready to work.

  - ERROR: well-defined "non-working" state; in principle ready to go (or try
    again), but user action or acknowlegement is required.

  - FATAL: undefined error state; no recovery possible, power cyle
    necessary (possibly for the Synchro, too, but at least restart-cycle of
    the application necessary).

'''

class SynchronizerEngine:
    ''' Engine class (i.e. state machine) for setting a pump-probe delay.

    This assumes the presence of the following:
    
      - A synchronizer mechanism. Typically this is ensured by a device
        akin to the Menlo Synchro RRE (a device which receives an external
        pace frequency and tunes the firing frequency of a laser to the
        external pace).
    
      - A delay shifter, i.e. a device which provides one or more tuning
        parameters, for specific ranges of delays, that we can change
        in order to move the delay. This is typically ensured by a device
        like the Menlo DDS-120, but we're using an `emmi.eda.MockMotor`
        interface here.

      - (A delay readback. This is typically ensured by a timed diode /
        photon counter / delay histogram device. The PicoQuant HydraHarp
        (or similar) devices can do this, but an oscilloscope can, too.
        Technically, in most beamlines this is a component of its own,
        but here we hide all that behind the Motor interface.)
    

    For some of the above we provide specific hardware support, but all
    of the above should (will?) be supported as generic EPICS PVs, too.
    '''

    STATE_START = "START"
    STATE_INIT = "INIT"
    STATE_SYNCED = "SYNCED"
    STATE_STRAY = "STRAY"
    STATE_OFF = "OFF"
    STATE_ERROR = "ERROR"
    STATE_FAIL = "FAIL"
    
    def __init__(self, sync_device, auto_stray=False, sync_timeout=5):
        ''' Initializes the sync-tracking state machine.

        The basic idea is that we follow the Menlo Syncro as closely as
        possible, but try to interfere as little as possible. What we want
        to know, essentially, is whether the box is in a synchronized state,
        so we can update delay, or not (so we wait or trigger an auto-sync).

        Args:
            sync_device: The device that provides sync-state feedback
              (and, possibly, action). Currently this should be a string
              device name (e.g. "/dev/ttyUSB0") of the Menlo Syncro RRE device.
        
            auto_stray: whether to automatically attempt straying (i.e. enter
              the STRAY state from OFF, without user interaction)
        
            sync_timeout: only useful where automatic synchronization is
              implemented. This is the timeout to wait for a synchronization
              attempt before we delcare it a failure.
        
        '''
        self.sync_device = sync_device
        
        self.sync_attempt_timeout = sync_timeout # seconds
        self.error_list = []

        # set True to to start sync, False to stop sync, and None to ignore
        self.auto_stray = auto_stray
        self.sync_request = None

        # For the state machine
        self.state = self.STATE_START
        self.old_state = self.STATE_START


    def stray(self):
        ''' Clears the system for an OFF->STRAY passing. '''
        self.sync_request = True


    def clear(self):
        ''' Clears current error list (only local, not device). '''
        self.error_list = []


    def push_error(self, error):
        ''' Adds `error` to the error list. '''
        self.error_list.append(error)


    @property
    def last_error(self):
        return self.error_list[-1]

        
    async def update(self):
        ''' Executes one state-loop step '''

        try:
            
            state_proc = getattr(self, f"state_{self.state}")
            entering = (self.state != self.old_state)

            if entering:
                logger.info(f'{self.old_state} -> {self.state}')
                if hasattr(self, f"enter_{self.state}"):
                    enter_proc = getattr(self, f"enter_{self.state}")
                    r = await enter_proc()
                    if r is not None:
                        raise RuntimeError(f'State entering procs not allowed to switch states')
                    new_state = self.state
                else:
                    logger.debug(f'State {self.state}: no dedicated enter proc, '
                                  f'using state_proc')
                    new_state = await state_proc()
            elif state_proc is not None:
                new_state = await state_proc()
            else:
                logger.error(f'Oops: {self.state} has no proc')

            self.old_state = self.state

            if new_state is not None:
                self.state = new_state
                
        except Exception as e:
            logger.error(f'Syncro state: {e}')
            logger.error(traceback.format_exc())
            raise
                

    async def loop(self, period=None):
        ''' Runs main state loop.

        Args:
            period: if not None (the default), the loop period parameter
              from .__init__() is being overwritten.
        '''
        
        slow_warn = True
        slow_cnt = 10
                
        while True:
            t0 = time.time()
            
            await self.update()
            
            tdiff = time.time()-t0
            if period > tdiff:
                tsleep = (period - tdiff)
            else:
                slow_cnt -= 1
                if slow_cnt <= 1 and slow_warn == True:
                    logger.warn(f'ACHTUNG, loop step is very slow ({tdiff} seconds).'
                                f'Will silence this warning after this.')
                    slow_warn = False
                tsleep = 0.001
                
            await asyncio.sleep(tsleep)


    async def state_START(self):
        ''' Connect to Menlo Syncro. '''
        return self.STATE_INIT


    async def state_INIT(self):
        ''' Check whether PID loop is closed or not.

        If the PID loop is closed, we enter SYNCED. Otherwise we
        need user approval before we move to STRAY.
        '''
        
        logger.info(f'Sync flags: {self.sync_device.flags}')

        if self.sync_device.synced:
            return self.STATE_SYNCED
        
        logger.debug(f'Resitual state is not SYNCED, requesting stop now')
        return self.STATE_OFF


    async def state_OFF(self):
        # stay here until user says "sync!"
        if self.auto_stray:
            self.stray()
        if self.sync_request == True:
            return self.STATE_STRAY
        return self.STATE_OFF

    
    async def enter_STRAY(self):
        self.sync_attempt_start = time.time()
        self.sync_request = None
        

    async def state_STRAY(self):
        if (self.sync_attempt_timeout >= 0) and \
           ((time.time() - self.sync_attempt_start) > self.sync_attempt_timeout):
            return self._ERROR(f'Sync timeout')

        # Simple case: just wait for sync to magically appear        
        if self.sync_device.synced:
            return self.STATE_SYNCED
        

    async def state_SYNCED(self):

        if not self.sync_device.synced:
            logger.debug(f'Lost sync state')
            return self._ERROR(f'Sync lost; flags: {self.sync_device.flags}')

        ## Apparently this isn't always required for SYNC?!...
        ## There are sporadic jumps out of ACTIVE -- Mattahias knows why -- but
        ## the system still counts as synchronized.

        #trk_state = TrackerState[self.hrt_root.TRACKER0.STATE()]
        #if trk_state not in [ "ACTIVE" ]:
        #    logger.debug(f'Tracker not active -> desync')
        #    self._error_append(f'Tracker inactive: {trk_state}')
        #    return self.STATE_ERROR

        # user requested stop
        if self.sync_request == False:
            return self.STATE_OFF

    
    def _ERROR(self, err):
        ''' Convenience wrapper to call `.push_error()` and return `.STATE_ERROR`. '''
        self.push_error(err)
        return self.STATE_ERROR


    async def enter_ERROR(self):
        if len(self.error_list) > 0:
            for i,err in enumerate(self.error_list):
                logger.error(f'Error {i+1}/{len(self.error_list)}: {err}')
        else:
            logger.error(f'We are in ERROR state, but no error object filed')
            self.error_list.append(None)


    async def state_ERROR(self):
        if len(self.error_list) == 0:
            logger.info(f'Error list clear, advancing to OFF')
            await self.sync_device.clear()
            return self.STATE_OFF
        return self.STATE_ERROR


    async def state_FAIL(self):
        logger.error(f'Failure')
        return self.STATE_FAIL
