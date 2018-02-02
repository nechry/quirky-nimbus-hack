# -*- coding: latin-1 -*-
#!/usr/bin/env python

import smbus
import sys
from sys import argv

bus = smbus.SMBus(1)
# nimbus i2c address
address = 0x25
# gauge 1 data register
register = 0xC8
# define gauge position from first argv
data = [int(argv[1][2:], 16), 0x00]
# try to write to i2c 
bus.write_i2c_block_data(address, register, data)
