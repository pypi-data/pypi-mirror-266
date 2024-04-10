#!/usr/bin/python3

#from emmi.scpi import MagicHuber
import sys

from caproto.asyncio.server import run as ca_run
from caproto.asyncio.server import start_server, Context

import logging, asyncio
logger = logging.getLogger(__name__)

import caproto as ca
import pyvisa
from parse import parse

from functools import partial, partialmethod

from emmi.scpi import MagicScpi

from kronos.ioc import KronosIoc

from os import environ
from os import path

class Application:
    
    def __init__(self, prefix=None, host=None, port=None, dev=None, rman="@py", args = None):
        if args is None:
            args = []

        self.prefix = prefix or environ.get('DG645_EPICS_PREFIX', "KMC3:XPP:DG645:")
        
        if dev is not None and rman is not None:
            pydev = { 'dev': dev,
                      'rman': rman }
        else:

            # if port is specified, we connect to a raw socket
            if port is not None:
                pydev = { 'dev': dev or environ.get('DG645_VISA_DEV',
                                                    f'TCPIP::{ls_host}::{ls_port}::SOCKET'),
                          'rman': rman or environ.get('DG645_VISA_RMAN', '@py') }        
            elif environ.get('KRONOS_SIM', 'no') == "yes":
                # use a simulated device.
                sim_path = environ.get('KRONOS_SIM_FILE', './test/visa-sim-dg645.yml')
                logger.info(f'Using simulated device from: {sim_path}')
                if not path.exists(sim_path):
                    logger.error(f'ACHTUNG, {sim_path} does not exist -- this will likely fail!')
                pydev = {
                    'dev': 'TCPIP::kronos-sim::INSTR',
                    'rman': f'{sim_path}@sim'
                }
            else:
                # otherwise we take the INSTR of KMC3
                ls_host = host or environ.get('DG645_HOST', '172.16.58.160')
                pydev = { 'dev': dev or environ.get('DG645_VISA_DEV',
                                                    f'TCPIP::{ls_host}::INSTR'),
                          'rman': rman or environ.get('DG645_VISA_RMAN',
                                                      '@py') }
        
        logger.debug(f"Connecting to DG645 {pydev['dev']} via '{pydev['rman']}'")
        self.ioc = KronosIoc(self.prefix, **pydev)
        

    async def async_run(self):
        
        logger.info(f'Starting IOC, PV list following')
        
        for pv in self.ioc.full_pvdb:
            logger.info(f"  {pv}")

        await start_server(self.ioc.full_pvdb)
