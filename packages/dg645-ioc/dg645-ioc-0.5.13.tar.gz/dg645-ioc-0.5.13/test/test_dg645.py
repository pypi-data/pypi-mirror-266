#!/usr/bin/python3

import pytest
import pyvisa
import parse
from emmi import scpi

from os import environ

import random

@pytest.fixture
def kronos_device():
    ''' Returns a test device to use. '''

    if environ.get('KRONOS_SIM', 'no') == 'yes':
        # Virtual device
        return {
            'resource_manager': 'test/visa-sim-dg645.yml@sim',
            #'device': 'ASRL1::INSTR',
            'device': 'TCPIP::kronos-sim::INSTR',
            'device_conf': {
                'read_termination': '\r\n',
                'write_temrination': '\r\n'
            }
        }
    else:
        # Real device
        return {
            'resource_manager': '@py',
            'device': 'TCPIP::172.16.58.160::5025::SOCKET',
            'device_conf': {
                'read_termination': '\r\n',
                'write_temrination': '\r\n'
            }
        }


def test_device(kronos_device):

    dev = scpi.MagicScpi(**kronos_device)

    print(f'Testing with device: {dev.query("*IDN?")}')

    v = random.randint(0, 1000)
    print(f'CH0 delay start: {dev.query("DLAY? 0")}, setting to {v}')
    dev.write(f"DLAY 2,0,{v}")
    dq = dev.query("DLAY? 2")
    print(f'Delay query: {dq}')
    assert float(dq.split(',')[1]) == v

    #print(f'Display: {dev.query("DISP? {}")}')

    print(f'Trigger mode: {dev.query("ADVT?")}')
