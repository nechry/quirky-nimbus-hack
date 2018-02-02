# -*- coding: latin-1 -*-
#!/usr/bin/env python

import smbus
import time
import sys
import random

NIMBUS_TEXT_MAX_WIDTH	=  41

addrGaugeCtrl = 0x25
addrGaugeDataCW = [0xC8, 0xE8, 0xA8, 0x88, 0x0F]
addrGaugeDataCCW = [0xD8, 0xF8, 0xB8, 0x98, 0x0F]
addrDispCtrl =  [0x74, 0x7C, 0x78, 0x70]
addrDispData =  [0x76, 0x7E, 0x7A, 0x72]

#
# Send char to i2c bus
#
def myi2cWrite(bus, addr, val):
	try:
		bus.write_byte(addr, val)
#        print("i2c sent addr=",hex(addr)," val=",hex(val))
		return 1
	except:
		print("i2c error: addr=", hex(addr), " val=", hex(val))
	return 0

#
# Send data block to i2c bus 
#
def myi2cWriteBlock(bus, addr, addr2, data):
	try:
		bus.write_i2c_block_data(addr, addr2, data)
		return 1
	except:
		print("i2c error: addr=",hex(addr), " addr2=", hex(addr2), " val=", hex(data[0]))
		return 0

#
#send char and retry once
#
def myi2cWriteWithRetry(bus, addr, val):
	written = myi2cWrite(bus, addr, val)
	if(written == 0):
		written = myi2cWrite(bus, addr, val)
		#print("retry")
		if(written == 0):
			return 0
	return 1

#
# Send data block to i2c bus and retry once
#
def myi2cWriteBlockWithRetry(bus, addr, addr2, data):
	written = myi2cWriteBlock(bus, addr, addr2, data)
	if(written == 0):
		written = myi2cWriteBlock(bus, addr, addr2, data)
		#print("retry")
		if(written == 0):
			return 0
	return 1

#
# Print out a 5x7 character of the selected character on the selected display
#
def printchar (bus, addrCadran, char, remainingLen):
    ordchar = ord(char)		# Get the ascii position of the char.
    written = 0    
    if( remainingLen <= 0):
		print "not enough space remaining on display", hex(addrCadran)
		return 0
    if (ordchar < 0x20):
		print "char out of range, too low"
		return 0
    if (ordchar >= 0x7F):
		print "char out of range, too high"
		return 0

    firstcol = (ordchar - 0x20) * 6

    #handle the maximum length of Nimbus
    allowedLen = min(remainingLen, fonttable[firstcol])

    #print each vertical line of the selected character 
    for col in range (1, allowedLen+1):
		line = fonttable[firstcol + col]
		ret = myi2cWriteWithRetry(bus, addrCadran,line)	
		#if one retry failed, return to try again
		if(ret == 0):
			return 0
		#increment counter
		written += ret	

    #add one vartical empty line between chars, if we still have space
    if(written < remainingLen):
		ret = myi2cWriteWithRetry(bus, addrCadran,0)
		written += ret

    #returns the number of pixels width written
    return written


#
# Fills display with spaces with remaining pixels
#
def fillDisplay (bus, addrCadran, remainingLen):
	#print each vertical line of the selected character
	for cpt in range (0, remainingLen):
		ret = myi2cWrite(bus, addrCadran,0)
		#retry once on errors
		if(ret == 0):
			ret = myi2cWrite(bus, addrCadran, 0)
	return


#
# 5x7 font, optimized for Nimbus (most chars are 3 pixels width)
#
fonttable = [
	0x01, 0x00, 0x00, 0x00, 0x00, 0x00,      # Code for char Space 
        0x01, 0x7D, 0x00, 0x00, 0x00, 0x00,      # Code for char !
        0x05, 0x70, 0x60, 0x00, 0x70, 0x60,      # Code for char "
        0x05, 0x24, 0x7E, 0x24, 0x7E, 0x24,      # Code for char #
        0x04, 0x12, 0x6A, 0x2B, 0x24, 0x00,      # Code for char $
        0x05, 0x63, 0x64, 0x08, 0x13, 0x63,      # Code for char %
        0x05, 0x36, 0x49, 0x35, 0x02, 0x05,      # Code for char &
        0x02, 0x70, 0x60, 0x00, 0x00, 0x00,      # Code for char '
        0x02, 0x3E, 0x41, 0x00, 0x00, 0x00,      # Code for char (
        0x02, 0x41, 0x3E, 0x00, 0x00, 0x00,      # Code for char )
        0x05, 0x08, 0x3E, 0x1C, 0x3E, 0x08,      # Code for char *
        0x05, 0x08, 0x08, 0x3E, 0x08, 0x08,      # Code for char +
        0x02, 0x01, 0x06, 0x00, 0x00, 0x00,      # Code for char ,
        0x03, 0x08, 0x08, 0x08, 0x00, 0x00,      # Code for char -
        0x01, 0x01, 0x00, 0x00, 0x00, 0x00,      # Code for char .
        0x04, 0x04, 0x08, 0x10, 0x20, 0x00,      # Code for char /
        0x03, 0x3E, 0x41, 0x3E, 0x00, 0x00,      # Code for char 0
        0x03, 0x21, 0x7F, 0x01, 0x00, 0x00,      # Code for char 1
        0x03, 0x47, 0x49, 0x31, 0x00, 0x00,      # Code for char 2
        0x03, 0x22, 0x49, 0x36, 0x00, 0x00,      # Code for char 3
        0x03, 0x1C, 0x24, 0x7F, 0x00, 0x00,      # Code for char 4
        0x03, 0x79, 0x49, 0x46, 0x00, 0x00,      # Code for char 5
        0x03, 0x3E, 0x49, 0x26, 0x00, 0x00,      # Code for char 6
        0x03, 0x40, 0x4F, 0x70, 0x00, 0x00,      # Code for char 7
        0x03, 0x36, 0x49, 0x36, 0x00, 0x00,      # Code for char 8
        0x03, 0x32, 0x49, 0x3E, 0x00, 0x00,      # Code for char 9
        0x01, 0x14, 0x00, 0x00, 0x00, 0x00,      # Code for char :
        0x02, 0x01, 0x16, 0x00, 0x00, 0x00,      # Code for char ;
        0x03, 0x08, 0x14, 0x22, 0x00, 0x00,      # Code for char <
        0x03, 0x14, 0x14, 0x14, 0x00, 0x00,      # Code for char =
        0x03, 0x22, 0x14, 0x08, 0x00, 0x00,      # Code for char >
        0x03, 0x20, 0x4D, 0x30, 0x00, 0x00,      # Code for char ?
        0x04, 0x3E, 0x49, 0x55, 0x3D, 0x00,      # Code for char @
        0x03, 0x3F, 0x44, 0x3F, 0x00, 0x00,      # Code for char A
        0x03, 0x7F, 0x49, 0x36, 0x00, 0x00,      # Code for char B
        0x03, 0x3E, 0x41, 0x41, 0x00, 0x00,      # Code for char C
        0x03, 0x7F, 0x41, 0x3E, 0x00, 0x00,      # Code for char D
        0x03, 0x7F, 0x49, 0x49, 0x00, 0x00,      # Code for char E
        0x03, 0x7F, 0x48, 0x48, 0x00, 0x00,      # Code for char F
        0x04, 0x3E, 0x41, 0x49, 0x4E, 0x00,      # Code for char G
        0x03, 0x7F, 0x08, 0x7F, 0x00, 0x00,      # Code for char H
        0x03, 0x41, 0x7F, 0x41, 0x00, 0x00,      # Code for char I
        0x04, 0x46, 0x41, 0x7F, 0x40, 0x00,      # Code for char J
        0x03, 0x7F, 0x08, 0x77, 0x00, 0x00,      # Code for char K
        0x03, 0x7F, 0x01, 0x01, 0x00, 0x00,      # Code for char L
        0x05, 0x7F, 0x20, 0x10, 0x20, 0x7F,      # Code for char M
        0x04, 0x7F, 0x10, 0x08, 0x7F, 0x00,      # Code for char N
        0x04, 0x3E, 0x41, 0x41, 0x3E, 0x00,      # Code for char O
        0x03, 0x7F, 0x48, 0x30, 0x00, 0x00,      # Code for char P
        0x04, 0x3E, 0x41, 0x45, 0x3E, 0x00,      # Code for char Q
        0x03, 0x7F, 0x48, 0x37, 0x00, 0x00,      # Code for char R
        0x03, 0x31, 0x49, 0x46, 0x00, 0x00,      # Code for char S
        0x03, 0x40, 0x7F, 0x40, 0x00, 0x00,      # Code for char T
        0x04, 0x7E, 0x01, 0x01, 0x7E, 0x00,      # Code for char U
        0x03, 0x7E, 0x01, 0x7E, 0x00, 0x00,      # Code for char V
        0x05, 0x7E, 0x01, 0x06, 0x01, 0x7E,      # Code for char W
        0x03, 0x77, 0x08, 0x77, 0x00, 0x00,      # Code for char X
        0x03, 0x78, 0x07, 0x78, 0x00, 0x00,      # Code for char Y
        0x04, 0x47, 0x49, 0x51, 0x61, 0x00,      # Code for char Z
        0x02, 0x7F, 0x41, 0x00, 0x00, 0x00,      # Code for char [
        0x03, 0x30, 0x08, 0x06, 0x00, 0x00,      # Code for char BackSlash
        0x02, 0x41, 0x7F, 0x00, 0x00, 0x00,      # Code for char ]
        0x03, 0x20, 0x40, 0x20, 0x00, 0x00,      # Code for char ^
        0x03, 0x01, 0x01, 0x01, 0x00, 0x00,      # Code for char _
        0x02, 0x60, 0x10, 0x00, 0x00, 0x00,      # Code for char `
        0x03, 0x17, 0x15, 0x0F, 0x00, 0x00,      # Code for char a
        0x03, 0x3F, 0x05, 0x02, 0x00, 0x00,      # Code for char b
        0x03, 0x06, 0x09, 0x09, 0x00, 0x00,      # Code for char c
        0x03, 0x02, 0x05, 0x1F, 0x00, 0x00,      # Code for char d
        0x03, 0x06, 0x0D, 0x05, 0x00, 0x00,      # Code for char e
        0x03, 0x08, 0x3F, 0x48, 0x00, 0x00,      # Code for char f
        0x03, 0x3B, 0x2B, 0x3F, 0x00, 0x00,      # Code for char g
        0x03, 0x1F, 0x04, 0x03, 0x00, 0x00,      # Code for char h
        0x01, 0x17, 0x00, 0x00, 0x00, 0x00,      # Code for char i
        0x03, 0x02, 0x11, 0x5E, 0x00, 0x00,      # Code for char j
        0x03, 0x3F, 0x04, 0x1B, 0x00, 0x00,      # Code for char k
        0x02, 0x3E, 0x01, 0x00, 0x00, 0x00,      # Code for char l
        0x05, 0x0F, 0x08, 0x06, 0x08, 0x07,      # Code for char m
        0x03, 0x0F, 0x08, 0x07, 0x00, 0x00,      # Code for char n
        0x03, 0x06, 0x09, 0x06, 0x00, 0x00,      # Code for char o
        0x03, 0x1F, 0x14, 0x08, 0x00, 0x00,      # Code for char p
        0x03, 0x08, 0x14, 0x1F, 0x00, 0x00,      # Code for char q
        0x03, 0x07, 0x08, 0x08, 0x00, 0x00,      # Code for char r
        0x03, 0x09, 0x15, 0x12, 0x00, 0x00,      # Code for char s
        0x03, 0x1E, 0x09, 0x09, 0x00, 0x00,      # Code for char t
        0x03, 0x0E, 0x01, 0x0F, 0x00, 0x00,      # Code for char u
        0x03, 0x0E, 0x01, 0x0E, 0x00, 0x00,      # Code for char v
        0x05, 0x0E, 0x01, 0x06, 0x01, 0x0E,      # Code for char w
        0x03, 0x1B, 0x04, 0x1B, 0x00, 0x00,      # Code for char x
        0x03, 0x19, 0x05, 0x1E, 0x00, 0x00,      # Code for char y
        0x03, 0x13, 0x15, 0x19, 0x00, 0x00,      # Code for char z
        0x03, 0x08, 0x3E, 0x41, 0x00, 0x00,      # Code for char {
        0x01, 0x7F, 0x00, 0x00, 0x00, 0x00,      # Code for char |
        0x03, 0x41, 0x3E, 0x08, 0x00, 0x00,      # Code for char }
        0x04, 0x20, 0x40, 0x20, 0x40, 0x00,      # Code for char ~
        0x04, 0x1E, 0x32, 0x62, 0x32, 0x00       # Code for char 127
]

#
# Class to handle the Nimbus
#
class NimbusMaster:
	def __init__(self):
		self.bus = smbus.SMBus(1)
		self.currentGVal = [0, 0, 0, 0]
		self.GValMax = [100, 100, 100, 100]
		self.GValMin = [0, 0, 0, 0]

	def nimbus_init(self):
		#init code (when wifi is off) => doesnt seems to work
		for i in range(0, 4):
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0xE2)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x20)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0xC0)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x8D)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0xEB)
			myi2cWriteBlockWithRetry(self.bus, addrDispCtrl[i], 0x81, [0x30])
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i] ,0xB5)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0xA1)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x31)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x46)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x2D)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x85)
			myi2cWriteBlockWithRetry(self.bus, addrDispCtrl[i], 0xF2, [0x00])
			myi2cWriteBlockWithRetry(self.bus, addrDispCtrl[i], 0xF3, [0x07])
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x90)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0xAF)
			myi2cWriteWithRetry(self.bus, addrDispCtrl[i], 0x40)
		#init displays
		for i in range(0, 4):		
			self.printText(i, " ")
		#init gauges
		myi2cWriteBlockWithRetry(self.bus, addrGaugeCtrl, addrGaugeDataCW[4], [0x0, 0x0])
		#wait for gauges
		time.sleep(2)
		
	#print text on the selected display (number 0 to 3)
	def subPrintText(self, numCadran, text):
		#set the register we want to write to
		myi2cWriteWithRetry(self.bus, addrDispCtrl[numCadran], 0xB0)
		myi2cWriteWithRetry(self.bus, addrDispCtrl[numCadran], 0x10)
		myi2cWriteWithRetry(self.bus, addrDispCtrl[numCadran], 0x00)
		#send the string, 41 pixels width max
		cpt = 0
		for ch in text:
 			written = printchar (self.bus, addrDispData[numCadran], ch, NIMBUS_TEXT_MAX_WIDTH-cpt)
			if(written == 0):
				return 0
			cpt += written		
		#fills up with spaces, if needed
		if(cpt < NIMBUS_TEXT_MAX_WIDTH):
			fillDisplay(self.bus, addrDispData[numCadran], NIMBUS_TEXT_MAX_WIDTH-cpt)		
		return 1
	
	#print text on the selected display (number 0 to 3), handles 3 complete retry
	def printText(self, numCadran, text):
		if(self.subPrintText(numCadran, text) == 0):
			if(self.subPrintText(numCadran, text) == 0):
				time.sleep(0.05)
				if(self.subPrintText(numCadran, text) == 0):
					print("text retry 3 times!!")
	
	#print text on the selected display (number 0 to 3) at selected place
	def printTextAt(self, numCadran, text, xpos):
		#set the register we want to write to
		myi2cWriteWithRetry(self.bus, addrDispCtrl[numCadran], 0xB0)
		myi2cWriteWithRetry(self.bus, addrDispCtrl[numCadran], 0x10)
		myi2cWriteWithRetry(self.bus, addrDispCtrl[numCadran], xpos)
		#send the string, 41 pixels width max
		cpt = xpos
		for ch in text:
 			written = printchar (self.bus, addrDispData[numCadran], ch, NIMBUS_TEXT_MAX_WIDTH - cpt)
			cpt += written		

	#set gauge mini and maxi
	def setGaugeMinMaxVal(self, numGauge, minv, maxv):
		self.GValMax[numGauge] = maxv
		self.GValMin[numGauge] = minv

	#set gauge value (predefined) on the selected gauge (0 to 3) on selected direction
	def setGaugeValueAndWay(self, numGauge, val, way):
		vmin = self.GValMin[numGauge]
		vmax = self.GValMax[numGauge]
		if(val < vmin):
			val = vmin
		if(val > vmax):
			val = vmax
		#translate the value into nimbus (270 degree)
		rawval = ((val - vmin) * 135) / (vmax - vmin)
		#starts at bottom
		rawval -= 67
		#inverse val
		rawval = -rawval
		#handle negative angles
		if(rawval < 0):
			rawval = 180 + rawval
		#set raw data
		self.setRawGaugeValueAndWay(numGauge, rawval, way)

	#set gauge RAW value (0 to 180 = 360degree) on the selected gauge (0 to 3) on selected direction
	def setRawGaugeValueAndWay(self, numGauge, val, way):
		data = [val, 0x0]
		#choose direction to move to: clockwise or counterclockwise
		if(way == 1):
			myi2cWriteBlockWithRetry(self.bus, addrGaugeCtrl, addrGaugeDataCW[numGauge], data)
		else:
			myi2cWriteBlockWithRetry(self.bus, addrGaugeCtrl, addrGaugeDataCCW[numGauge], data)
	
	#set gauge value (predefined) and try to determine the best direction
	def setGaugeValue(self, numGauge, val):
		lastv = self.currentGVal[numGauge]
		#check delta to determine gauge direction
		delta = val - lastv
		if(delta < 0):
			self.setGaugeValueAndWay(numGauge, val, 0)
		else:
			self.setGaugeValueAndWay(numGauge, val, 1)
		#save new value
		self.currentGVal[numGauge] = val
