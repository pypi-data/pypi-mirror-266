#!/usr/bin/python3

import logging
logger = logging.getLogger(__name__)

from caproto.server import pvproperty, PVGroup
from caproto import ChannelType

class SyncronizerIoc(PVGroup):
    ''' EPICS access to the Synconizer state machine.
    '''
    state = pvproperty(max_length=40, dtype=ChannelType.STRING, doc="Synchronizer state")
    error = pvproperty(max_length=40, dtype=ChannelType.STRING, doc="Current error")
    clear = pvproperty(value=0, doc="Set to 1 to clear current errors")
    stray = pvproperty(value=0, doc="Set to 1 to manually pass into STRAY from OFF")

    def __init__(self, prefix, syncro):
        ''' Initialize the syncster IOC

        Args:
          prefix: the EPICS prefix
        
          syncro: the syncster state machine
        
        '''
        super().__init__(prefix)
        self.syncro = syncro

    @property
    def full_pvdb(self):
        return self.pvdb


    async def _update_pv(self, pv, new_value):
        old_value = pv.value[0] if hasattr(pv.value, "__len__") else pv.value
        if new_value != old_value:
            return await pv.write(new_value)


    async def update(self):
        ''' Updates the IOC variables according to the Syncster state. '''
        
        await self._update_pv(self.state, self.syncro.state)
        
        if self.syncro.state in [ self.syncro.STATE_ERROR,
                                  self.syncro.STATE_FAIL ]:
            await self._update_pv(self.error, self.syncro.last_error)


    @state.startup
    async def state(self, instance, asynclib):
        pass

    
    @clear.putter
    async def clear(self, inst, val):
        if val == 1:
            self.syncro.clear()
            await self._update_pv(self.clear, 0)


    @stray.putter
    async def stray(self, inst, val):
        if val == 1:
            self.syncro.stray()
            await self._update_pv(self.stray, 0)
            
