#!/usr/bin/python3

from kronos.main import main as ioc_main
import time

import multiprocessing as mp
mp.set_start_method('fork')

from caproto.sync.client import read as ca_read, write as ca_write
from caproto import CASeverity

import pytest, asyncio, sys, os

now = time.time()

def start_ioc():
    
    p = mp.Process(target=ioc_main, args=[])

    ## daemon mode will ensure that IOC exits when main process exits
    
    p.daemon = True
    p.start()

    print(f'Giving the IOC time to come up...')
    time.sleep(2)
    print(f'I guess we\'re moving: {p}')
    
    return p

@pytest.mark.asyncio
async def test_ioc():
    #
    # VERY basic IOC test: essentially just makes sure the IOC
    # fires up, finds a device (by env-vars), and reacts to all PVs
    # that we know of.
    #
    
    ioc = start_ioc()

    prefix = 'KMC3:XPP:DG645:'

    # single-instance variables (i.e. once per device, not per channel)
    ro_variables = ['update', 'err:last_RBV' ]

    # write-only variables, not tested: err:clear, pres:load, pres:save

    # these also need to have an _RBV to access
    rw_variables = [ 'trig:src', 'trig:lvl', 'trig:intrate', ]
    for c in range(1,5):
        rw_variables += [ f'ch{c}:div', f'ch{c}:dly', f'ch{c}:dur',
                          f'ch{c}:ampl', f'ch{c}:pol', f'ch{c}:offs' ]

    for v in ro_variables:
        print(f'{time.time()-now}: Querying: {prefix}{v}')
        s = ca_read(f'{prefix}{v}')
        print(f'{time.time()-now}:   got {v}: {s.data[0]}')
        assert s.status.severity == CASeverity.SUCCESS
        #await asyncio.sleep(0.1)
    
    for v in rw_variables:
        print(f'{time.time()-now}: Querying: {prefix}{v}')
        s = ca_read(f'{prefix}{v}')
        d = s.data[0]
        print(f'{time.time()-now}:   got {v}: {d}')
        assert s.status.severity == CASeverity.SUCCESS
        print(f'{time.time()-now}: Writing: {prefix}{v} -> {d}')
        w = ca_write(f'{prefix}{v}', d)
        #await asyncio.sleep(0.1)
        
