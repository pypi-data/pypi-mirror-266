#!/usr/bin/python3

from caproto.server import pvproperty, PVGroup
from caproto import ChannelType
import logging, asyncio, time
from emmi import scpi
logger = logging.getLogger(__name__)

from os import environ

class Dg645PropertyBase(object):
    ''' Base class for all DG645 relate PVGroups
    '''
    
    def __init__(self, device):
        '''
        Args:        
            device: a MagicScpi / PropertyNode instance to use for communication
              with the device.

            root_node: instead of a device, 
        '''
        self.device = device

        # pyvisa-sim is buggy AF, async SCPI doesn't work.
        # We need to actually implement a reasonable (about 1 ms)
        # poll timeout
        if environ.get('KRONOS_SIM', 'no') == "yes":
            self.scpi_poll_timeout = 0.1
        else:
            self.scpi_poll_timeout = 0

        # Register the MagickScpi / PropertyNodes for each property
        self.var_nodes = { }


    def addNode(self, pvinst, name=None, **node_args):
        if name is None:
            name = pvinst.pvspec.name
        self.var_nodes[name] = scpi.PropertyNode(dev=self.device.kdev, name=name,
                                                 lock=self.device.device_lock,
                                                 **node_args)

    def node(self, name):
        return self.var_nodes[name]


    @property
    def full_pvdb(self):
        return self.pvdb

    
    async def general_putter(self, inst, val):
        await self.var_nodes[inst.pvspec.name].async_set(val)


    async def update_if_new(self, new_value, pvobj=None, pvname=None):
        ## Sends an update through EPICS only if new_value differs from the old one
        if pvobj is None:
            pvobj = getattr(self, f'{var}_RBV')
        if pvobj.value != new_value:
            await pvobj.write(new_value)


    async def update(self): 
        '''
        Performs one state update operation a.k.a. device readout.
        '''

        pv_data = {}
        for var,node in self.var_nodes.items():
            if not node.can_get():
                continue
            pv_rbv_obj = getattr(self, f'{var}_RBV')
            try:
                data = await node.async_get(poll_timeout=self.scpi_poll_timeout)
            except Exception as e:
                logger.error(f'Error reading {var}: {str(e)}')
                raise
            
            pv_data[pv_rbv_obj] = data
        
        await asyncio.gather(*[self.update_if_new(d, pvobj=v) for v,d in pv_data.items()])
        


class Dg645ChannelPVGroup(PVGroup, Dg645PropertyBase):
    
    div     = pvproperty(dtype=ChannelType.LONG, doc="Trigger divider")
    div_RBV = pvproperty(dtype=ChannelType.LONG, doc="Trigger divider readback")
    
    dly     = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse start (in nanoseconds), measured from trigger",)
    dly_RBV = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse start (in nanoseconds) readback",)
    
    dur     = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse duration in nanoseconds",)
    dur_RBV = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse duration (readback)",)
    
    ampl     = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse level amplitude in V",)
    ampl_RBV = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse level amplitude in V (readback)",)

    offs     = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse level offset in V")
    offs_RBV = pvproperty(dtype=ChannelType.FLOAT, doc="Pulse level offset in V (readback)")

    pol      = pvproperty(doc="Polarity of output (NEG/POS)",
                          dtype=ChannelType.ENUM,
                          enum_strings=["NEG", "POS"],
                          record = "bi")

    pol_RBV = pvproperty(dtype=ChannelType.ENUM,
                         enum_strings=["NEG", "POS"],
                         doc="Readback value of output polarity")


    def __init__(self, prefix, device, channel):
        '''
        Args:
            prefix: the EPICS prefix to pass on to PVGroup. May contain `{channel}`
              to generate a specific per-channel prefix.
        
            device: a MagicScpi / PropertyNode instance to use for communication
              with the device
        
            channel: the channel mnemonic. Used for 
        '''

        Dg645PropertyBase.__init__(self, device)
        
        self.prefix = prefix.format(channel=channel)
        self.channel_id = channel
        logger.debug(f'Channel {channel}, EPICS prefix {self.prefix}')
        
        super().__init__(self.prefix)

        # Register the MagickScpi / PropertyNodes for each property
        
        self.addNode(self.div,
                     setter_fmt=f"PRES {channel},"+"{}",
                     getter_fmt=f"PRES? {channel}",
                     cast=lambda x: int(x))
        
        self.addNode(self.dly,
                     setter_fmt=f"DLAY {channel*2},0,"+"{}",
                     getter_fmt=f"DLAY? {channel*2}",
                     unwrap=None,
                     cast=lambda x: float(x.split(",")[1]),
                     pack=lambda x: x)
            
        self.addNode(self.dur,
                     setter_fmt=f"DLAY {channel*2+1},{channel*2},"+"{}",
                     getter_fmt=f"DLAY? {channel*2+1}",
                     unwrap=None,
                     cast=lambda x: float(x.split(",")[1]),
                     pack=lambda x: x)
            
        self.addNode(self.ampl,
                     setter_fmt=f"LAMP {channel},"+"{}",
                     getter_fmt=f"LAMP? {channel}",
                     cast=lambda x: float(x))
            
        self.addNode(self.offs,
                     setter_fmt=f"LOFF {channel},"+"{}",
                     getter_fmt=f"LOFF? {channel}",
                     cast=lambda x: float(x))
            
        self.addNode(self.pol,
                     setter_fmt=f"LPOL {channel},"+"{data}",
                     getter_fmt=f"LPOL? {channel}",
                     pack=lambda x: { 'POS': 1, 'NEG': 0}[x.upper()])


    @div.putter
    async def div(self, inst, val):
        if val > 0:
            return await self.general_putter(inst, val)

    @dly.putter
    async def dly(self, inst, val):
        if val >= 0:
            return await self.general_putter(inst, val)

    @dur.putter
    async def dur(self, inst, val):
        if val > 0:
            return await self.general_putter(inst, val)

    @ampl.putter
    async def ampl(self, inst, val): return await self.general_putter(inst, val)

    @offs.putter
    async def offs(self, inst, val): return await self.general_putter(inst, val)

    @pol.putter
    async def pol(self, inst, val): return await self.general_putter(inst, val)


class Dg645TriggerPVGroup(PVGroup, Dg645PropertyBase):
    ''' Implements trigger functionality
    '''

    lvl =      pvproperty(dtype=ChannelType.FLOAT, doc="Trigger level threshold in (V)")
    
    lvl_RBV =  pvproperty(dtype=ChannelType.FLOAT, doc="Readback value of trigger level threshold in (V)")

    # device-dependent
    src =     pvproperty(dtype = ChannelType.ENUM,
                         enum_strings = ["INTERNAL", "RISING", "FALLING"],
                         doc = "Trigger edge")
    
    src_RBV = pvproperty(dtype = ChannelType.ENUM,
                         enum_strings=["INTERNAL", "RISING", "FALLING"],
                         doc = "Trigger edge: 0 -- internal trigger, 1 -- rising edge, 2 -- falling edge")
    
    intrate =      pvproperty(dtype=ChannelType.FLOAT, doc="Trigger frequency (Hz) for internal trigger")
    
    intrate_RBV =  pvproperty(dtype=ChannelType.FLOAT, doc="Readback for internal trigger frequency")


    def __init__(self, prefix, device):
        Dg645PropertyBase.__init__(self, device)
        self.prefix = prefix
        super().__init__(self.prefix)
        
        self.adv_trigger = scpi.PropertyNode(dev=self.device.kdev, name='adv',
                                             setter_fmt="ADVT {data}",
                                             getter_fmt="ADVT?",
                                             lock=self.device.device_lock)
        self.adv_trigger.set(1)

        self.addNode(self.lvl, setter_fmt="TLVL {}", getter_fmt="TLVL?")
        self.addNode(self.src, setter_fmt="TSRC {}", getter_fmt="TSRC?")
        self.addNode(self.intrate, setter_fmt="TRAT {}", getter_fmt="TRAT?")
        

    @lvl.putter
    async def lvl(self, inst, val): return await self.general_putter(inst, val)

    @src.putter
    async def src(self, inst, val): return await self.general_putter(inst, val)
    


class Dg645PresetPVGroup(PVGroup, Dg645PropertyBase):
    ''' Functionality for loading / saving of configuration presets.
    This is highly instrument specific. For instruments that don't
    have a built-in presetting function, one can be emulated per software.
    '''    
    save = pvproperty(dtype=ChannelType.STRING,
                      doc="Save instrument settings to location X")
    load = pvproperty(dtype=ChannelType.STRING,
                      doc="Restore instrument settings from location X")
    
    def __init__(self, prefix, device, load_on_start=None):
        ''' Preset loading / saving functionlity.

        This is based in SCPI commands `*RCL` and `*SAV`. They usually receive
        a token as a preset memory pointer. We don't interpret the token, we
        just pass it on to the device (which is why the PV type is STRING).

        If `load_on_start` is not `None`, then on initialization the device
        is instructed to load that specific preset.
        '''
        Dg645PropertyBase.__init__(self, device)
        self.prefix = prefix
        super().__init__(self.prefix)
        
        self.addNode(self.load, name="load", setter_fmt="*RCL {}", getter_fmt=None)
        self.addNode(self.save, name="save", setter_fmt="*SAV {}", getter_fmt=None)

        if load_on_start is not None:
            logger.info(f'Auto-loading preset: {load_on_start}')
            self.node("load").set(load_on_start)
        

    @load.putter
    async def load(self, inst, val): return await self.general_putter(inst, val)

    @save.putter
    async def save(self, inst, val): return await self.general_putter(inst, val)



class Dg645ExtrasPVGroup(PVGroup, Dg645PropertyBase):
    # CAL = pvproperty(val = "0",
    #                  dtype = ChannelType.STRING,
    #                  doc = "Runs auto calibration routine",)
    pass
    

class Dg645ErrorPVGroup(PVGroup, Dg645PropertyBase):
    ''' Error handling
    '''
    last_RBV =  pvproperty(doc="Last error", max_length=40, dtype=ChannelType.STRING)
    clear = pvproperty(dtype=ChannelType.LONG, doc="Clear instrument errors when set to 1, then resets to 0",)

    def __init__(self, prefix, device):
        Dg645PropertyBase.__init__(self, device)
        self.prefix = prefix
        super().__init__(self.prefix)
        
        self.addNode(self.last_RBV, name="last", setter_fmt=None, getter_fmt=f"LERR?")
        self.addNode(self.clear, setter_fmt="*CLS", getter_fmt=None)


    @clear.putter
    async def clear(self, inst, val):
        if val == 1:
            logger.info(f'Clearing errors')
            await self.general_putter(inst, val)
            return 0
