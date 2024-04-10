#!/usr/bin/python3

from emmi.eda import MotorEngine

class DdsMotor:
    ''' Low-level delay-setting device with the the DDS-120.

    Do not use this class directly, use `DelayDdsDevice` instead.

    This is an `emmi.eda.MockMotor` compatible device, supporting
    all of the `emmi` motor API. Additionally, it has an `.update()`
    async function that needs to be called regularly for updating
    state.

    The DDS-120 doesn't have an actual delay read-back mechanism,
    so we're using an external object with an async `.update()`
    function of its own (that we call regularly from our own `.update()`)
    and a single property, `.delay`, that we can read.
    '''

    def __init__(self, dds_obj, delay_rbck,
                 phase_limit=1e-9,
                 rad_per_sec=1e-9,
                 detune_freq=5.0):
        ''' Receives a `diddy` compatible DDS-120 object to use for delay setting.

        Args:
            dds_obj: a `diddy` compatible DDS-120 object
        
            delay_rbck: a delay-readback device with an async `.update()`
              and a `.delay` property.
        
            phase_limit: delay deltas smaller than this will be processed
              using the DDS-120 phase modifyer; deltas larger whill be
              processed by detuning the fequency by the given amount of
              Hertz `detune_freq` and waiting for the delay to drift.

            rad_per_sec: factor for phase-based shifting: radians per second.

            detune_freq: how much to detune the frequency for frequency-based
              delay shifting. The value will be used as-is for positive delay
              deltas, and multiplied by -1 for negative deltas.
        '''
        self.dds = dds_obj

        dds_fw = self.dds.firmwareVersion
        dds_serial = self.dds.serialNumber
        logger.info(f"DDS-120: serial {dds_serial}, f/w v{dds_fw}")
                

        # This is actually a small state machine ("IDLE" / "PHASING" / "DETUNING")


    async def update(self):
        ''' Update state and commands.

        This is the only function that actually communicates with the DDS-120.
        '''
        pass


class DdsDelayDevice(MotorEngine):
    ''' Delay-setting engine with the DDS-120.

    Uses `DelayDdsMotor` under the hood. This uses a simple state machine
    (see `emmi.eda.MotorEngine` for details) to ensure that no conflicting
    commands are accepted. You are *highly* encouraged to use this instead
    of using the `DelayDdsMotor` directly.
    '''

    def __init__(self, motor):

        # FIXME: how to we deal with the double-action shift+phase for
        # large shifts?!
        super().__init__(motor)
