#!/usr/bin/python3

import asyncio
from syncster_ioc.main import main as ioc_main

import time

import multiprocessing as mp
#mp.set_start_method('fork')

from caproto.sync.client import read as ca_read, write as ca_write
from caproto import CASeverity

import pytest, asyncio, sys, os, random, string

now = time.time()

class TestIoc:

    @pytest.fixture(scope="class", autouse=True)
    def prefix(self):
        p = ''.join(random.choice(string.ascii_lowercase) \
            for i in range(6))
        print(f'Test IOC prefix: {p}')
        return p

    
    @pytest.fixture(scope="class", autouse=True)
    def ioc(self, prefix):
        p = mp.Process(target=ioc_main, args=[f'{prefix}:', True])
        p.daemon = True
        p.start()
        print(f'Giving the IOC time to come up...')
        time.sleep(3)
        print(f'I guess we\'re moving: {p}')
        return p


    # cheap take just to make sure we have a PV to read out in the
    # first place
    @pytest.mark.asyncio
    async def test_state(self, ioc, prefix):
        await asyncio.sleep(0.5)
        r = ca_read(f'{prefix}:state').data[0].decode('utf-8')
        assert r == 'SYNCED'


