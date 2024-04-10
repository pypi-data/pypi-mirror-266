#!/usr/bin/python3

import logging

class OrthogonalFlagsMap:
    '''
    This is a mapping helper for various flags-to-strings facilities
    (Harp warnings, Harp flags, ...) encoded as a i.e. a bitwise field
    of *several* items. You can iterate through the warnings to reach
    all of them:
    ```
       >>> warn = OrthogonalFlagsMap(HarpWarnings, 0x441)
       >>> [ warn.text(w) for w in warn ]
       [ 'Sync rate is zero', 'Input rate is too high', 'Time span is too small' ]
       >>> warn.INPT_RATE_ZERO
       True
       >>> warn.INPT_RATE_TOO_HIGH
       False
    ```
    '''
    
    def __init__(self, flagsMap, code=None):
        '''
        Initializes the mapper. Parameters:
          - `code`: This is a bitwise field of flags that this instance represents.
          - `flagsMap`: This is a dictionary which maps single string keys to
            `(flagMask, flagDescription)` tuples. The string key part
            is a non-changeable string that describes the flags for all eternity,
            and which the user (or other program layers) can use to access the flag.
            `flagDescription` is a human-readable string which can change, e.g.
            by translation or a more precise specification, and `flagMask` is a bit
            mask that indicates whether the flag is set or not.
        '''
        self.flagsMap = flagsMap
        
        if not isinstance (flagsMap, dict):
            t = type(flagsMap)
            raise RuntimeError(f'Flags map needs to be a dictionary, received'+
                               f' {t}: {flagsMap}')

        if len(flagsMap) == 0:
            logging.debug(f'Flags map is empty: f{flagsMap}')
        else:
            first = next(iter(flagsMap))
            if not isinstance(flagsMap[first], tuple) or \
               2 != len(flagsMap[first]):
                raise RuntimeError(f'Flags map value needs to be a (key, description)'+
                                   f' tuple; got {flagsMap[first]} instead')
            
        if code is not None:
            self.recode(code)
    
    def recode(self, code):
        '''
        Resets the code to `code` and returns a reference to self.
        This is to update the active/inactive flags list to the
        ones encoded in `code` without altering the identity of the
        object.
        '''
        self.code = code
        return self

    def __str__(self):
        return str([f for f in self.keys()])

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, key):
        return (self.code & self.flagsMap[key][0]) != 0

    def __iter__(self):
        ''' Iterate through all warnings encoded in `self.code`. '''
        for k,v in self.flagsMap.items():
            if (v[0] & self.code) != 0:
                yield k

    def keys(self):
        '''
        Mimic a bit of a `dict`-like interface: return all the HHLIB API
        warning keys that are encoded in `self.code`.
        '''
        for k in self:
            yield k

    def items(self):
        '''
        Mimic a bit more a `dict`-like interface: return all the HHLIB API
        warning keys that are encoded in `self.code`.
        '''
        for k,v in self.flagsMap.items():
            if (v[0] & self.code):
                yield (k, v[1])
    
    def __getitem__(self, flag):
        ''' Another way of reading a flag '''
        return self.__getattr__(flag)

    def text(self, flag):
        '''
        Returns the description text.
        '''
        return self.flagsMap.get(flag, None)[1]

    def mask(self, flag):
        '''
        Returns the numerical mask value.
        '''
        return self.flagsMap.get(flag, None)[0]

    def __len__(self):
        return len([i for i in self.items()])

#
# Flag map names must match the data type reported by PHAROS!
# The first round of keys can be chosen freely, but the number
# relates to the number of parameters reported by Pharos.
#


INSR = {
    'TRIG':         (0x01, "Triggered"),
    'RATE':         (0x02, "Got a trigger while a delay or burst was in progress"),
    'END_OF_DELAY': (0x04, "A delay cycle has completed"),
    'END_OF_BURST': (0x08, "A burst cycle has completed"),
    'INHIBIT':      (0x10, "A trigger or output delay cycle was inhibited"),
    'ABORT_DELAY':  (0x20, "A delay cycle was aborted early"),
    'PLL_UNLOCK':   (0x40, "The 100 MHz PLL came unlocked"),
    'RB_UNLOCK':    (0x80, "The installed Rb oscillator is unlocked"),
}

ESR = {
    'OPC':  (0x01, "Operation complete"),
    'res1': (0x02, "Reserved"),
    'QYE':  (0x04, "Query error"),
    'DDE':  (0x08, "Device dependent error"),
    'EXE':  (0x10, "Execution error"),
    'CME':  (0x20, "Command error"),
    'res2': (0x40, "Reserved"),
    'PON':  (0x80, "Power on"),
}

#TUNEST
