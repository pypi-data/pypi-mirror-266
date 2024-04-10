EPICS-IOC for the Stanford DG645 Delay Generator
================================================

![release](https://gitlab.com/kmc3-xpp/kronos-ioc/-/badges/release.svg) 
![pipeline](https://gitlab.com/kmc3-xpp/kronos-ioc/badges/release/pipeline.svg)
![coverage](https://gitlab.com/kmc3-xpp/kronos-ioc/badges/release/coverage.svg)


Quickstart
----------

### In a System Shell

#### Obtaining

Download via PyPI: `pip install dg645-ioc` or via GitLab:

   ```
   git clone https://gitlab.com/kmc3-xpp/kronos-ioc
   ```

#### Running from the command line

Configure at least the IP address and the EPICS prefix and start via shell:

   ```
   $ export DG645_EPICS_PREFIX="BEAMLINE:DG645:"
   $ export DG645_HOST="10.0.0.17"
   $ dg645-ioc
   INFO:kronos.ioc:Stanford Research Systems,DG645,s/n001776,ver1.14.10E
   INFO:root:Starting IOC, PV list following
   [...]
   INFO:caproto.ctx:Server startup complete.
   ```

### In a Container

#### Obtaining a Container


You can download the automatically generated container:

   ```
   podman pull registry.gitlab.com/kmc3-xpp/kronos-ioc:latest
   ```

...or create your own, assuming  you've downloaded the sources into `./kronos-ioc`:

   ```
   $ podman build -t kronos-ioc -f kronos-ioc/Dockerfile -v $PWD/kronos-ioc:/kronos_src:z
   ```

#### Running in Podman / Docker

Start as a Podman container (Docker should work the same, just replace thed
`podman` command by `docker`):

   ```
   $ podman run -ti --rm \
       --env DG645_EPICS_PREFIX="BEAMLINE:DG645:" \
	   --env DG645_HOST=10.0.0.17\
	   --name dg645-ioc \
	   --net=host \
	   kronos-ioc:latest
   ```
   Note that we're using host networking in the example above to
   integrate into an existing EPICS network as mindlessly as possible.
   If you care (as you should) for security and access control,
   you might want to think about an more elaborate deployment,
   e.g. using Wireguard interfaces or CAgateway access control.
   
 - Assuming that you've installed the EPICS userland tools, access
   your PVs using `caget`, `caput` and `camonitor` as you're used to:
   ```
   $ caget BEAMLINE:DG645:ch4:dly_RBV
   BEAMLINE:DG645:ch4:dly_RBV        3.14
   ```

Configuration
-------------

 Here's a list of environment variables that might help:
 
- `DG645_HOST`: host name or IP of the DG645 controller
  
- `DG645_PORT`: this is better left blank (the default). In that
  case, the IOC will create a "`TCPIP::<host>::INSTR`" PyVISA device
  name. If the port is specified, it will create a
  "`TCPIP::<host>::<ip>::SOCKET`" device name instead.
  
- `DG645_VISA_DEV`: PyVISA device to connecto to, instead of the
  TCP/IP device. If set, overrides host/port.
	
- `DG645_VISA_RMAN`: PyVISA resource manager. Defaults to `"@py"`.
  If you've got this far, you know what this is good for ;-)
	
- `DG645_EPICS_PREFIX`: EPICS PV prefix to use. Include trailing column
  (`:`) if you need one. Defaults to `KMC3:XPP:DG645:`.
	
- `DG645_LOGGING`: one of `error`, `warn`, `info` or `debug`. Defaults
  to `info`.
	
- `DG645_LOG_STATUS`: if set to `yes`, the IOC will periodically
  (about once per second) log the
  current status of all variables it observes to the `info` logging
  acility. The default is not to do that.
	

EPICS Variables
---------------

The IOC exports the following variables. To all of these the
desginated prefix (`$DG645_EPICS_PREFIX`) needs to be prepended.

Main IOC control and flow variables:

- `update`: used to drive the main query loop. When read, returns
  an integer value which is being continuously increased on
  every device readout (all readback values are read out regularly,
  quasi-simultaneously, typically 1 up to 4 times per second).

The presets device module:

- `pres:load`: when a string is written to this, the corresponding
   preset is loaded. This is typically an instrument-specific feature.
   on the DG645, `0` is loading instrument defaults, and `1` to `9`
   are user-addressable slots.

- `pres:save`: when a string is written to this, current settings are
  saved to the corresponding slot.
	
	
The error device module (for error handling)

- `err:last_RBV`: string representation of the latest device error.
- `err:clear`: when 1 is written here, the errors are cleared
  (typically using a `*CLS` SCPI command)
	
	
Trigger device module variables:

- `trig:lvl`: set the trigger channel level.
- `trig:lvl_RBV`: readback value for trigger channel level
- `src`: trigger source. Currently `"RISING"` and `"FALLING"`
  are supported for the corresponding edges of the external
  trigger pulse, and `"INTERNAL"` (on DG645) for an automated
  internal trigger
- `src_RBV`: trigger source readback.
- `intrate`: trigger rate for internal trigger (in Hz)
- `intrate_RBV`: readback for the internal trigger frequency.


Channel specific variables: the DG645 has 4 channels, labeled
`1`, `2`, `3` and `4`, respectively. Other devices may have
different labels (when and if supported). For every channel,
the following set of variables is exported. `{label}` designates
the channel label, e.g. `ch{label}...` for channel 4 would be
`ch4...`:

- `ch{label}:dly`: start of the delay, in seconds, from the
  trigger pulse
- `ch{label}:dur`: pulse duration in seconds
- `ch{label}:div`: pulse divider (i.e. which N-th pulse to
  trigger for)
- `ch{label}:ampl`: pulse amplitude in V
- `ch{label}:offs`: pulse offset in V
- `ch{label}:pol`: pulse polarity, can be one of `"POS"` or `"NEG"`.
- `ch{label}:..._RBV`: each of the variables above publishes
  its readback value in the corresponding `_RBV` PV.


Caveats & Bugs
--------------

Might kick your dog, empty your fridge, and run off with your
girlfriend.

Otherwise enjoy! :-D
