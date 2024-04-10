#!/usr/bin/python3

from caproto.asyncio.server import Context
from syncster_ioc.syncro_engine import SynchronizerEngine
from syncster_ioc.syncro_ioc import SyncronizerIoc

from syncster_ioc.delay_dds import DdsDelayDevice
from syncster_ioc.sync_rre import RreSyncDevice

import logging, asyncio
logger = logging.getLogger("syncster_ioc")

from os import environ

class SyncsterApplication:

    def __init__(self, prefix, rre_port=None, engine_params=None):
        ''' Initializes the Syncster-IOC application.

        Args:
            prefix: EPICS prefix (including the trailing ':')
        
            rre_port: tty device name for communication with the
              Menlo Syncro RRE. Default will be extracted from
              `$SYNCSTER_PREFIX` if not specified.
        
            engine_params: additional named parameters to pass
              to the SynchronizerEngine. A number of environment
              variables will be used for defaults if none are
              specified.
        '''

        if rre_port is None:
            rre_port = environ.get('SYNCSTER_RRE_PORT', "")

        if rre_port in (None, "", "none", "None"):
            logger.info(f'Using mock sync-device')
            from syncster_ioc.sync_mock import MockSyncDevice
            self.rre_device = MockSyncDevice()
        else:
            logger.info(f'Want Syncro box: {rre_port}')
            self.rre_device = RreSyncDevice(rre_port)

        if engine_params is None:
            engine_params = {
                'auto_stray': environ.get('SYNCSTER_AUTO_STRAY', 'no') == "yes",
                'sync_timeout': int(environ.get('SYNCSTER_SYNC_TIMEOUT', '300'))
            }
            logger.info(f'Syncster engine parameters: {engine_params}')
            
        self.sync_engine = SynchronizerEngine(self.rre_device, **engine_params)
        self.ioc = SyncronizerIoc(prefix, self.sync_engine)

    
    async def run(self, period=1.0):

        logger.info(f'Exporting PVs:')
        for pv in self.ioc.full_pvdb:
            logger.info(f'  {pv}')
        
        ctx = Context(self.ioc.full_pvdb)
        ioc_task = asyncio.create_task(ctx.run())
        
        while True:
            r = await asyncio.gather(*[
                self.rre_device.update(),
                self.sync_engine.update(),
                self.ioc.update(),
                asyncio.sleep(period),
            ], return_exceptions=False)
