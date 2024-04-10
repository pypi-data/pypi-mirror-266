#!/usr/bin/python3

import pytest

from syncster_ioc.syncro_engine import SynchronizerEngine
from syncster_ioc.sync_mock import MockSyncDevice

from emmi.eda import MockMotor, MotorEngine

import asyncio

@pytest.fixture(scope="class", autouse=True)
def device():
    return MockSyncDevice()

@pytest.fixture(scope="class", autouse=True)
def engine(device):
    # Create a designated mock-engine (i.e. a "real" engine based on a
    # mock sync-device).  Need this to be able to trigger errors on demand.
    return SynchronizerEngine(device)

class EngineRunner:
    def __init__(self, engine):
        self.engine = engine
        
    async def __aenter__(self):
        #print(f'{self.engine}: starting loop task')
        self.task = asyncio.create_task(self.engine.loop(period=0.01))
        return self.engine

    async def __aexit__(self, *args):
        #print(f'{self.engine}: ending loop task')
        try:
            self.task.cancel()
            await self.task
        except asyncio.CancelledError:
            pass

@pytest.fixture(scope="class", autouse=True)
def engine_runner(engine):
    return EngineRunner(engine)


class _TestSyncronizerEngine:
    # Testing the states of the sync-engine, using fake devices.
    # All test in this class use the _same_ engine

    def test_boo(self, engine):
        print(f"Engine state #3 {engine} -> {engine.state}")

    def test_hoo(self, engine):
        print(f"Engine state #4 {engine} -> {engine.state}")


@pytest.mark.asyncio
async def test_synced(engine_runner):
    async with engine_runner as engine:
        await asyncio.sleep(1.0)
        assert engine.state == "SYNCED"


@pytest.mark.asyncio
async def test_off(engine_runner, device):
    async with engine_runner as engine:
        device.pretend_synced(False)
        await asyncio.sleep(0.5)
        assert engine.state == "OFF" ## waiting for stray

@pytest.mark.asyncio
async def test_stray(engine_runner, device):
    async with engine_runner as engine:
        device.pretend_synced(False)
        await asyncio.sleep(0.5)
        engine.stray()
        await asyncio.sleep(0.5)
        assert engine.state == "STRAY"


@pytest.mark.asyncio
async def test_findsync(engine_runner, device):
    async with engine_runner as engine:
        
        device.pretend_synced(False)
        await asyncio.sleep(0.5)
        assert engine.state == "OFF"
        
        engine.stray()
        await asyncio.sleep(0.5)
        assert engine.state == "STRAY"
        
        device.pretend_synced(True)
        await asyncio.sleep(0.5)
        assert engine.state == "SYNCED"

        
@pytest.mark.asyncio
async def test_unsync_error(engine_runner, device):
    async with engine_runner as engine:
        await asyncio.sleep(0.5)
        assert engine.state == "SYNCED"

        device.pretend_synced(False)
        await asyncio.sleep(0.5)
        assert engine.state == "ERROR"
        assert engine.last_error != None

        engine.clear()
        await asyncio.sleep(0.5)
        assert engine.state == "OFF"

        engine.stray()
        await asyncio.sleep(0.5)
        assert engine.state == "STRAY"
        
        device.pretend_synced(True)
        await asyncio.sleep(0.5)
        assert engine.state == "SYNCED"
