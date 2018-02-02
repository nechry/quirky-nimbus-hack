# quirky-nimbus-hack
Quirky Nimbus Hacking files

base on work from [Edu Garcia's](http://blog.arcnor.com/quirky-nimbus-hacking/)

and initial [mynimbus.py](https://github.com/r0bin-fr/pirok/blob/master/mynimbus.py) script thank' to Matt

# Software Setup #
## SPI on Pi ##
The SPI peripheral is not turned on by default. To enable it, do the following.

* Run **sudo raspi-config**.
* Use the down arrow to select **5 Interfacing Options**
* Arrow down to **P5 I2C**.
* Select **yes** when it asks you to enable I2C,
* Use the right arrow to select the **<Finish>** button.
* Select **yes** when it asks to *reboot*.
  
### check if I2C is loaded ###
Check if your I2C bus is loaded
```
ls /dev/i2c-*
```
Expected get something like: **/dev/i2c-1**

## Set Baud rate ##
Important the Raspberry PI I2C baudrate must set to **400KHz** to match imp002 baudrate.
use :
```
sudo nano /boot/config.txt
```
and add
```
dtparam=i2c_baudrate=400000
```
if not present and *reboot* the RPI

## Libraries ##
First update apt package manager
```
sudo apt-get update
sudo apt-get upgrade
```
Install command-line utility programs that can help get an I2C interface
```
sudo apt-get install -y i2c-tools
```

#Hardware Setup#
I directly solder cables on the board imp002 to simplify the connection to the I2C bus of the Raspberry PI.

## I2C bus wiring ##

imp002 I2C PCB pins
* SDA => 14
* SCL => 22
* GND => 1

Raspberry PI I2C pins
* SDA => 3
* SCL => 5
* GND => 1

*The electric imp002 and Raspberry PI bas have 3.3Volts level. No level shifter board is required.*

### Detect the imp002 I2C address ###
```
sudo i2cdetect -y 1
```
You expect get address **0x25**, the I2C address of the imp002.
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- 25 -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```
