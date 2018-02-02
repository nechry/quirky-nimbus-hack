# quirky-nimbus-hack
Quirky Nimbus Hacking files

base on work from Edu Garcia's
http://blog.arcnor.com/quirky-nimbus-hacking-part-2/

and initial script 
https://github.com/r0bin-fr/pirok/blob/master/mynimbus.py

Important the Raspberry PI I2C baudrate must set to 400KHz

use :
```
sudo nano /boot/config.txt
```
and add
```
dtparam=i2c_baudrate=400000
```
if not present and reboot the RPI
