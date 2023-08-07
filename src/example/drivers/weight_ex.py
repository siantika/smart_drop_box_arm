import os
import time
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/weight'))

### real hardware
if '--hw-orpi' in sys.argv:
    import wiringpi 
    from wiringpi import GPIO

### mock for testing in native pc (arch-linux)
else:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(parent_dir, 'drivers/mock_wiringpi'))
    from mock_wiringpi import MockWiringPi 
    wiringpi = MockWiringPi()

from weight import HX711Driver
# Pins for HX711 module
PIN_DOUT = 9
PIN_PD_SCK = 10

referenceUnit = 142

def cleanAndExit():
    print("Cleaning...")       
    print("Bye!")
    sys.exit()

"""
    Create a weight object from HX711 module
    modified from: https://github.com/tatobari/hx711py/tree/master
"""
weight = HX711Driver(PIN_DOUT, PIN_PD_SCK) 

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.


# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
weight.set_reference_unit(referenceUnit)
weight.calibrate()
print("Tare done! Add weight now...")
while True:
    try:
        val = weight.get_weight(21)
        print(val)
        weight.power_down()
        weight.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
