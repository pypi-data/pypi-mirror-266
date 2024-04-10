#!/usr/bin/python3

from syncster import rbp, hrt
import traceback, logging

logger = logging.getLogger(__name__)

PidState = {
    0: "OFF",
    1: "HOLD",
    2: "PID_IN_LOW",
    3: "PID_IN_HIGH",
    4: "SETTLE",
    5: "LOCKED",
    6: "RELOCK",
    7: "LWOSC_MAGIC",
    8: "LWOSC_LOW",
    9: "LWOSC_HIGH"
}

PidMap = { v:k for k,v in PidState.items() }

TrackerState = {
    0: "OFF",     # inactive
    1: "DORMANT", # enabled, waiting for lock
    2: "SETTLING",
    3: "ACTIVE",
    4: "CORR_INC", # correction attempt, increasing position
    5: "CORR_DEC"  # correction attempt, decreasing position
}

TrackerMap = { v:k for k,v in TrackerState.items() }

class RreSyncDevice:
    ''' Sync Device for the `syncster.syncro.DelayEngine` based on Menlo Syncro RRE.

    The most important part is to provide acces to the sync state
    (synced / not-synced) and to the error state.
    '''
    
    def __init__(self, port):
        self.rbp = rbp.Device(port)

        hrt_dv = lambda vd: f"{vd['major']}.{vd['minor']}.{vd['patch']}.{vd['build']}"
        hrt_lv = lambda vl: ".".join([str(i) for i in vl])        

        self.hrt_root = hrt.NodeAccess(dev=self.rbp)
        rre_reg = self.hrt_root.RegVers()
        rre_hw = self.hrt_root.DEV.VerHW()
        rre_fw = self.hrt_root.DEV.VerFW()
        logger.info(f"Syncro RRE: HRT v{hrt_lv(rre_reg)}, h/w v{hrt_dv(rre_hw)}, f/w v{hrt_dv(rre_fw)}")

        self._state_info = {}

    async def update(self):
        ''' Readout procedure for the whole RRE Syncrho device object.

        The idea is that any property query will return cached data, and the
        data cache will be updated once per period (whatever that is) when
        this function is called.
        '''
        self._state_info['pid'] = PidState[self.hrt_root.LOCKBOX.PID.Status()]
        self._state_info['trk'] = TrackerState[self.hrt_root.TRACKER0.STATE()]


    async def clear(self):
        ''' If clearing errors is necessary, this procedure provides it. '''
        pass


    @property
    def synced(self):
        return self._state_info['pid'] == 'LOCKED'


    @property
    def errors(self):
        ''' Returns a list of current errors.
        
        Each error is an object with a useful human readable string
        representation. Can, but doesn't have to, a subclass of Exception.
        '''
        
        # Yeah, right... nope. Error readout currently not implemented,
        # simply put, because we don't know _what_ exactly to read out.
        # If you find yourself in the necessity of knowing about a specific
        # error, include it in the readout series in `.update()`, and return
        # the specific list here.
        #
        # The idea is tha we return the errors for as long as they persist.
        # There is a `.clear()` method for clearing errors, and it should
        # be used, but it will only be implemented if the underlying device
        # needs it.

        return []


    @property
    def flags(self):
        # Some useful information, mostly for debugging
        return [
            f"pid:{self._state_info['pid']}",
            f"trk:{self._state_info['trk']}",
        ]
        
