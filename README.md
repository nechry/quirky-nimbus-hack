# quirky-nimbus-hack
Quirky Nimbus Hacking files

base on work from [Edu Garcia's](http://blog.arcnor.com/quirky-nimbus-hacking/)

and initial [mynimbus.py](https://github.com/r0bin-fr/pirok/blob/master/mynimbus.py) script thank' to Matt

## Set Baud rate ##
Important the Raspberry PI I2C baudrate must set to *400KHz*

use :
```
sudo nano /boot/config.txt
```
and add
```
dtparam=i2c_baudrate=400000
```
if not present and reboot the RPI

## i2c bus wiring ##
The Raspberry PI I2C is directly connect to the IMP002 I2C

IMP002 I2C PCB pins
* SDA => 14
* SCL => 22
* GND => 1

Raspberry PI I2C pins
* SDA => 3
* SCL => 5
* GND => 1



### Detect the IMP002 I2C address ###
```
sudo i2cdetect -y 1
```
You expect get address *0x25* detected on the Imp002
