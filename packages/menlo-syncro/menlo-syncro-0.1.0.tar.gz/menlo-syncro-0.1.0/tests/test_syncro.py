#!/usr/bin/python3

from syncster.syncro import Syncro
from syncster import rbp
import asyncio, pytest

@pytest.fixture
def syncro_device():
    return  rbp.Device("/dev/ttyUSB0")

@pytest.mark.asyncio
async def test_states(syncro_device):

    s = Syncro(device=syncro_device)

    s.sync_request = True

    await s.loop(period=0.1)
        
