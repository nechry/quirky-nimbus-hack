# -*- coding: latin-1 -*-
# !/usr/bin/env python

import smbus
import time

NIMBUS_TEXT_MAX_WIDTH = 41

busAddress = 0x25
registerGaugeDataCW = [0xC8, 0xE8, 0xA8, 0x88, 0x0F]
registerGaugeDataCCW = [0xD8, 0xF8, 0xB8, 0x98, 0x0F]
registerDisplayControl = [0x74, 0x7C, 0x78, 0x70]
registerDisplayData = [0x76, 0x7E, 0x7A, 0x72]


#
# Send char to i2c bus
#
# noinspection PyBroadException
def i2c_write(bus, register, value):
    try:
        bus.write_byte(register, value)
        #        print("i2c sent register=",hex(register)," value=",hex(value))
        return 1
    except:
        print("i2c error: register=", hex(register), " value=", hex(value))
    return 0


#
# Send data block to i2c bus 
#
# noinspection PyBroadException
def i2c_write_block(bus, register, register2, data):
    try:
        bus.write_i2c_block_data(register, register2, data)
        return 1
    except:
        print("i2c error: register=", hex(register), " register2=", hex(register2), " value=", hex(data[0]))
        return 0


#
# send char and retry once
#
def i2c_write_with_retry(bus, register, value):
    written = i2c_write(bus, register, value)
    if written == 0:
        written = i2c_write(bus, register, value)
        # print("retry")
        if written == 0:
            return 0
    return 1


#
# Send data block to i2c bus and retry once
#
def i2c_write_block_with_retry(bus, register, register2, data):
    written = i2c_write_block(bus, register, register2, data)
    if written == 0:
        written = i2c_write_block(bus, register, register2, data)
        # print("retry")
        if written == 0:
            return 0
    return 1


#
# Print out a 5x7 character of the selected character on the selected display
#
def i2c_write_char(bus, register_dial, char, remaining_length):
    ord_char = ord(char)  # Get the ascii position of the char.
    written = 0
    if remaining_length <= 0:
        print "not enough space remaining on display", hex(register_dial)
        return 0
    if ord_char < 0x20:
        print "char out of range, too low"
        return 0
    if ord_char >= 0x7F:
        print "char out of range, too high"
        return 0
    first_column = (ord_char - 0x20) * 6
    # handle the maximum length of Nimbus
    allowed_length = min(remaining_length, font_table[first_column])
    # print each vertical line of the selected character
    for col in range(1, allowed_length + 1):
        line = font_table[first_column + col]
        retry = i2c_write_with_retry(bus, register_dial, line)
        # if one retry failed, return to try again
        if retry == 0:
            return 0
        # increment counter
        written += retry
    # add one vertical empty line between chars, if we still have space
    if written < remaining_length:
        retry = i2c_write_with_retry(bus, register_dial, 0)
        written += retry
    # returns the number of pixels width written
    return written


#
# Fills display with spaces with remaining pixels
#
def fill_display(bus, register_dial, remaining_length):
    # print each vertical line of the selected character
    for cpt in range(0, remaining_length):
        result = i2c_write(bus, register_dial, 0)
        # retry once on errors
        if result == 0:
            i2c_write(bus, register_dial, 0)
    return


#
# 5x7 font, optimized for Nimbus (most chars are 3 pixels width)
#
font_table = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00,  # Code for char Space
              0x01, 0x7D, 0x00, 0x00, 0x00, 0x00,  # Code for char !
              0x05, 0x70, 0x60, 0x00, 0x70, 0x60,  # Code for char "
              0x05, 0x24, 0x7E, 0x24, 0x7E, 0x24,  # Code for char #
              0x04, 0x12, 0x6A, 0x2B, 0x24, 0x00,  # Code for char $
              0x05, 0x63, 0x64, 0x08, 0x13, 0x63,  # Code for char %
              0x05, 0x36, 0x49, 0x35, 0x02, 0x05,  # Code for char &
              0x02, 0x70, 0x60, 0x00, 0x00, 0x00,  # Code for char '
              0x02, 0x3E, 0x41, 0x00, 0x00, 0x00,  # Code for char (
              0x02, 0x41, 0x3E, 0x00, 0x00, 0x00,  # Code for char )
              0x05, 0x08, 0x3E, 0x1C, 0x3E, 0x08,  # Code for char *
              0x05, 0x08, 0x08, 0x3E, 0x08, 0x08,  # Code for char +
              0x02, 0x01, 0x06, 0x00, 0x00, 0x00,  # Code for char ,
              0x03, 0x08, 0x08, 0x08, 0x00, 0x00,  # Code for char -
              0x01, 0x01, 0x00, 0x00, 0x00, 0x00,  # Code for char .
              0x04, 0x04, 0x08, 0x10, 0x20, 0x00,  # Code for char /
              0x03, 0x3E, 0x41, 0x3E, 0x00, 0x00,  # Code for char 0
              0x03, 0x21, 0x7F, 0x01, 0x00, 0x00,  # Code for char 1
              0x03, 0x47, 0x49, 0x31, 0x00, 0x00,  # Code for char 2
              0x03, 0x22, 0x49, 0x36, 0x00, 0x00,  # Code for char 3
              0x03, 0x1C, 0x24, 0x7F, 0x00, 0x00,  # Code for char 4
              0x03, 0x79, 0x49, 0x46, 0x00, 0x00,  # Code for char 5
              0x03, 0x3E, 0x49, 0x26, 0x00, 0x00,  # Code for char 6
              0x03, 0x40, 0x4F, 0x70, 0x00, 0x00,  # Code for char 7
              0x03, 0x36, 0x49, 0x36, 0x00, 0x00,  # Code for char 8
              0x03, 0x32, 0x49, 0x3E, 0x00, 0x00,  # Code for char 9
              0x01, 0x14, 0x00, 0x00, 0x00, 0x00,  # Code for char :
              0x02, 0x01, 0x16, 0x00, 0x00, 0x00,  # Code for char ;
              0x03, 0x08, 0x14, 0x22, 0x00, 0x00,  # Code for char <
              0x03, 0x14, 0x14, 0x14, 0x00, 0x00,  # Code for char =
              0x03, 0x22, 0x14, 0x08, 0x00, 0x00,  # Code for char >
              0x03, 0x20, 0x4D, 0x30, 0x00, 0x00,  # Code for char ?
              0x04, 0x3E, 0x49, 0x55, 0x3D, 0x00,  # Code for char @
              0x03, 0x3F, 0x44, 0x3F, 0x00, 0x00,  # Code for char A
              0x03, 0x7F, 0x49, 0x36, 0x00, 0x00,  # Code for char B
              0x03, 0x3E, 0x41, 0x41, 0x00, 0x00,  # Code for char C
              0x03, 0x7F, 0x41, 0x3E, 0x00, 0x00,  # Code for char D
              0x03, 0x7F, 0x49, 0x49, 0x00, 0x00,  # Code for char E
              0x03, 0x7F, 0x48, 0x48, 0x00, 0x00,  # Code for char F
              0x04, 0x3E, 0x41, 0x49, 0x4E, 0x00,  # Code for char G
              0x03, 0x7F, 0x08, 0x7F, 0x00, 0x00,  # Code for char H
              0x03, 0x41, 0x7F, 0x41, 0x00, 0x00,  # Code for char I
              0x04, 0x46, 0x41, 0x7F, 0x40, 0x00,  # Code for char J
              0x03, 0x7F, 0x08, 0x77, 0x00, 0x00,  # Code for char K
              0x03, 0x7F, 0x01, 0x01, 0x00, 0x00,  # Code for char L
              0x05, 0x7F, 0x20, 0x10, 0x20, 0x7F,  # Code for char M
              0x04, 0x7F, 0x10, 0x08, 0x7F, 0x00,  # Code for char N
              0x04, 0x3E, 0x41, 0x41, 0x3E, 0x00,  # Code for char O
              0x03, 0x7F, 0x48, 0x30, 0x00, 0x00,  # Code for char P
              0x04, 0x3E, 0x41, 0x45, 0x3E, 0x00,  # Code for char Q
              0x03, 0x7F, 0x48, 0x37, 0x00, 0x00,  # Code for char R
              0x03, 0x31, 0x49, 0x46, 0x00, 0x00,  # Code for char S
              0x03, 0x40, 0x7F, 0x40, 0x00, 0x00,  # Code for char T
              0x04, 0x7E, 0x01, 0x01, 0x7E, 0x00,  # Code for char U
              0x03, 0x7E, 0x01, 0x7E, 0x00, 0x00,  # Code for char V
              0x05, 0x7E, 0x01, 0x06, 0x01, 0x7E,  # Code for char W
              0x03, 0x77, 0x08, 0x77, 0x00, 0x00,  # Code for char X
              0x03, 0x78, 0x07, 0x78, 0x00, 0x00,  # Code for char Y
              0x04, 0x47, 0x49, 0x51, 0x61, 0x00,  # Code for char Z
              0x02, 0x7F, 0x41, 0x00, 0x00, 0x00,  # Code for char [
              0x03, 0x30, 0x08, 0x06, 0x00, 0x00,  # Code for char BackSlash
              0x02, 0x41, 0x7F, 0x00, 0x00, 0x00,  # Code for char ]
              0x03, 0x20, 0x40, 0x20, 0x00, 0x00,  # Code for char ^
              0x03, 0x01, 0x01, 0x01, 0x00, 0x00,  # Code for char _
              0x02, 0x60, 0x10, 0x00, 0x00, 0x00,  # Code for char `
              0x03, 0x17, 0x15, 0x0F, 0x00, 0x00,  # Code for char a
              0x03, 0x3F, 0x05, 0x02, 0x00, 0x00,  # Code for char b
              0x03, 0x06, 0x09, 0x09, 0x00, 0x00,  # Code for char c
              0x03, 0x02, 0x05, 0x1F, 0x00, 0x00,  # Code for char d
              0x03, 0x06, 0x0D, 0x05, 0x00, 0x00,  # Code for char e
              0x03, 0x08, 0x3F, 0x48, 0x00, 0x00,  # Code for char f
              0x03, 0x3B, 0x2B, 0x3F, 0x00, 0x00,  # Code for char g
              0x03, 0x1F, 0x04, 0x03, 0x00, 0x00,  # Code for char h
              0x01, 0x17, 0x00, 0x00, 0x00, 0x00,  # Code for char i
              0x03, 0x02, 0x11, 0x5E, 0x00, 0x00,  # Code for char j
              0x03, 0x3F, 0x04, 0x1B, 0x00, 0x00,  # Code for char k
              0x02, 0x3E, 0x01, 0x00, 0x00, 0x00,  # Code for char l
              0x05, 0x0F, 0x08, 0x06, 0x08, 0x07,  # Code for char m
              0x03, 0x0F, 0x08, 0x07, 0x00, 0x00,  # Code for char n
              0x03, 0x06, 0x09, 0x06, 0x00, 0x00,  # Code for char o
              0x03, 0x1F, 0x14, 0x08, 0x00, 0x00,  # Code for char p
              0x03, 0x08, 0x14, 0x1F, 0x00, 0x00,  # Code for char q
              0x03, 0x07, 0x08, 0x08, 0x00, 0x00,  # Code for char r
              0x03, 0x09, 0x15, 0x12, 0x00, 0x00,  # Code for char s
              0x03, 0x1E, 0x09, 0x09, 0x00, 0x00,  # Code for char t
              0x03, 0x0E, 0x01, 0x0F, 0x00, 0x00,  # Code for char u
              0x03, 0x0E, 0x01, 0x0E, 0x00, 0x00,  # Code for char v
              0x05, 0x0E, 0x01, 0x06, 0x01, 0x0E,  # Code for char w
              0x03, 0x1B, 0x04, 0x1B, 0x00, 0x00,  # Code for char x
              0x03, 0x19, 0x05, 0x1E, 0x00, 0x00,  # Code for char y
              0x03, 0x13, 0x15, 0x19, 0x00, 0x00,  # Code for char z
              0x03, 0x08, 0x3E, 0x41, 0x00, 0x00,  # Code for char {
              0x01, 0x7F, 0x00, 0x00, 0x00, 0x00,  # Code for char |
              0x03, 0x41, 0x3E, 0x08, 0x00, 0x00,  # Code for char }
              0x04, 0x20, 0x40, 0x20, 0x40, 0x00,  # Code for char ~
              0x04, 0x1E, 0x32, 0x62, 0x32, 0x00  # Code for char 127
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
        # init code (when wifi is off) => doesnt seems to work
        for i in range(0, 4):
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0xE2)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x20)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0xC0)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x8D)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0xEB)
            i2c_write_block_with_retry(self.bus, registerDisplayControl[i], 0x81, [0x30])
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0xB5)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0xA1)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x31)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x46)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x2D)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x85)
            i2c_write_block_with_retry(self.bus, registerDisplayControl[i], 0xF2, [0x00])
            i2c_write_block_with_retry(self.bus, registerDisplayControl[i], 0xF3, [0x07])
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x90)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0xAF)
            i2c_write_with_retry(self.bus, registerDisplayControl[i], 0x40)
        # init displays
        for i in range(0, 4):
            self.display_text(i, " ")
        # init gauges
        i2c_write_block_with_retry(self.bus, busAddress, registerGaugeDataCW[4], [0x0, 0x0])
        # wait for gauges
        time.sleep(2)

    # print text on the selected display (number 0 to 3)
    def i2c_display_text(self, dial_number, text):
        # set the register we want to write to
        i2c_write_with_retry(self.bus, registerDisplayControl[dial_number], 0xB0)
        i2c_write_with_retry(self.bus, registerDisplayControl[dial_number], 0x10)
        i2c_write_with_retry(self.bus, registerDisplayControl[dial_number], 0x00)
        # send the string, 41 pixels width max
        cpt = 0
        for ch in text:
            written = i2c_write_char(self.bus, registerDisplayData[dial_number], ch, NIMBUS_TEXT_MAX_WIDTH - cpt)
            if written == 0:
                return 0
            cpt += written
        # fills up with spaces, if needed
        if cpt < NIMBUS_TEXT_MAX_WIDTH:
            fill_display(self.bus, registerDisplayData[dial_number], NIMBUS_TEXT_MAX_WIDTH - cpt)
        return 1

    # print text on the selected display (number 0 to 3), handles 3 complete retry
    def display_text(self, dial_number, text):
        if self.i2c_display_text(dial_number, text) == 0:
            if self.i2c_display_text(dial_number, text) == 0:
                time.sleep(0.05)
                if self.i2c_display_text(dial_number, text) == 0:
                    print("text retry 3 times!!")

    # print text on the selected display (number 0 to 3) at selected place
    def display_text_at(self, dial_number, text, xpos):
        # set the register we want to write to
        i2c_write_with_retry(self.bus, registerDisplayControl[dial_number], 0xB0)
        i2c_write_with_retry(self.bus, registerDisplayControl[dial_number], 0x10)
        i2c_write_with_retry(self.bus, registerDisplayControl[dial_number], xpos)
        # send the string, 41 pixels width max
        cpt = xpos
        for ch in text:
            written = i2c_write_char(self.bus, registerDisplayData[dial_number], ch, NIMBUS_TEXT_MAX_WIDTH - cpt)
            cpt += written

    # set gauge mini and maxi
    def set_gauge_min_max(self, gauge_number, minimum_value, maximum_value):
        self.GValMax[gauge_number] = maximum_value
        self.GValMin[gauge_number] = minimum_value

    # set gauge value (predefined) on the selected gauge (0 to 3) on selected direction
    def set_gauge_value_and_way(self, gauge_number, value, way):
        minimum_value = self.GValMin[gauge_number]
        maximum_value = self.GValMax[gauge_number]
        if value < minimum_value:
            value = minimum_value
        if value > maximum_value:
            value = maximum_value
        # translate the value into nimbus (270 degree)
        raw_value = ((value - minimum_value) * 135) / (maximum_value - minimum_value)
        # starts at bottom
        raw_value -= 67
        # inverse value
        raw_value = -raw_value
        # handle negative angles
        if raw_value < 0:
            raw_value = 180 + raw_value
        # set raw data
        self.set_raw_gauge_value_way(gauge_number, raw_value, way)

    # set gauge RAW value (0 to 180 = 360degree) on the selected gauge (0 to 3) on selected direction
    def set_raw_gauge_value_way(self, gauge_number, value, way):
        data = [value, 0x0]
        # choose direction to move to: clockwise or counterclockwise
        if way == 1:
            i2c_write_block_with_retry(self.bus, busAddress, registerGaugeDataCW[gauge_number], data)
        else:
            i2c_write_block_with_retry(self.bus, busAddress, registerGaugeDataCCW[gauge_number], data)

    # set gauge value (predefined) and try to determine the best direction
    def set_gauge_value(self, gauge_number, value):
        last_value = self.currentGVal[gauge_number]
        # check delta to determine gauge direction
        delta = value - last_value
        if delta < 0:
            self.set_gauge_value_and_way(gauge_number, value, 0)
        else:
            self.set_gauge_value_and_way(gauge_number, value, 1)
        # save new value
        self.currentGVal[gauge_number] = value
