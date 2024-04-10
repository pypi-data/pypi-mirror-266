#!/usr/bin/python3

## Mock class compatible with the Synchronized API (see syncster_ioc.sync_rre).

class MockSyncDevice:

    def __init__(self, *args, **kwargs):
        self._pretend_synced = True

    async def update(self):
        pass

    async def clear(self):
        pass
    
    @property
    def synced(self):
        return self._pretend_synced

    @property
    def errors(self):
        return []

    @property
    def flags(self):
        return [ "MONKEY_DRUNK" ]


    ## API elements specifically for testing onlyl
    
    def pretend_synced(self, val):
        # set the pretend variable to synced / unsynced
        self._pretend_synced = val
