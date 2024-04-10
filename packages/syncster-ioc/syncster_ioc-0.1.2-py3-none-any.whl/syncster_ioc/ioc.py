#!/usr/bin/python3

import logging
logger = logging.getLogger(__name__)

from caproto.server import pvproperty, PVGroup
from caproto import ChannelType

from syncster_ioc.syncro_ioc import SyncronizerIoc

'''
The architecture is roughly as follows.

The main access / driving component is a Motor-like API (`emmi.eda.MotorEngine`)
that drives the delay. Behind the scenes there is typically a DDS-120 -- see
the `.delay...`-classes.

But using the DDS-120 as the delay motor bears two complications:

 1. The DDS-120 doesn't have a delay readback value. We need to get that
    from somewhere else (could be another device, but for now, we prefer
    to read that from a different PV)

 2. Accessing and commanding the delay "motor" only makes sense if and when
    the system is in a "synchronized" state -- typically driven by a Menlo
    Syncro RRE. So the delay "motor" needs to pay attention that the
    syncro-engine is in "SYNCED" state (and raise an error if it isn't).

Beyond this, there are 
The low(er)-level device access is done through the `.sync_...` classes.
'''

class SyncsterIoc(PVGroup):
    ''' EPICS access to the Syncster state machine.
    '''

    moo = pvproperty(value=0)

    def __init__(self, prefix, syncro):
        self.syncro_ioc = SyncronizerIoc(f'{prefix}SYNCRO:', syncro)
        super().__init__(prefix)


    @property
    def full_pvdb(self):
        db = self.pvdb.copy()
        db.update(self.syncro_ioc.pvdb)
        return db

    async def update(self):
        await self.syncro_ioc.update()
