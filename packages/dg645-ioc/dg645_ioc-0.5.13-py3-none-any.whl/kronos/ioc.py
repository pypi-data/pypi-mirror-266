#!/usr/bin/python3

from caproto.server import pvproperty, PVGroup
import logging, asyncio, time
import pyvisa
from parse import parse
from functools import partial, partialmethod
from emmi import scpi
import kronos.flags as tflg
from caproto import ChannelType

from kronos import channel

logger = logging.getLogger(__name__)

from os import environ

import traceback

class KronosIoc(PVGroup):
    
    update = pvproperty(value=0, doc="Update counter (increments with every readout)")
    

    def __init__(self, prefix, dev=None, rman=None, motors=None):

        self.dg645 = self._init_device(dev, rman)
        self.prefix = prefix
        
        super().__init__(prefix)

        self.update_counter = 1

        autoload_preset = environ.get("KRONOS_AUTOLOAD", None)
        if autoload_preset in [ "no", "false", "NO", "No", "0" ]:
            autoload_preset = None

        self.channels = [
            channel.Dg645ChannelPVGroup(prefix=f'{prefix}'+'ch{channel}:',
                                        device=self.dg645, channel=ch)
            for ch in range(1, 5)
        ]

        self.others = [
            channel.Dg645TriggerPVGroup(f'{prefix}trig:', self.dg645),
            channel.Dg645PresetPVGroup(f'{prefix}set:', self.dg645, load_on_start=autoload_preset),
            channel.Dg645ErrorPVGroup(f'{prefix}err:', self.dg645)
        ]


    def _init_device(self, dev=None, rman=None):

        # useful for reconnecting on errors
        if dev is None:
            dev = self.param_dev
        else:
            self.param_dev = dev
        
        if rman is None:
            rman = self.param_rman
        else:
            self.param_rman = rman
        
        dg645 = scpi.MagicScpi(device = dev,
                               resource_manager = rman,
                               device_conf = {
                                   "timeout": 500,
                                   "read_termination": "\r\n",
                                   "write_termination": "\r\n"
                               })

        helo = dg645.query("*IDN?")

        try:
            if "Stanford Research Systems,DG645,s/n" not in helo:
                logger.error(f'Unexpected device identifyer: "{helo}"')
                raise RuntimeError(f'Unexpected device identifyer: "{helo}"')
            self.dg645_version = helo[45:]
        except:
            raise RuntimeError(f'Cannot parse version from "{helo}"')
        
        logger.info(f'DG645 found, version: {self.dg645_version}')
        
        return dg645

    @property
    def full_pvdb(self):
        p = {}
        p.update(self.pvdb)
        for c in self.channels + self.others:
            p.update(c.full_pvdb)
        return p


    @update.scan(period=0.25, stop_on_error=True)
    async def _update(self, inst, async_lib):

        response = await asyncio.gather(*(
            [ch.update() for ch in self.channels] +
            [m.update() for m  in self.others] +
            [self.update.write(self.update_counter)]
        ), return_exceptions=False)

        self.update_counter += 1
