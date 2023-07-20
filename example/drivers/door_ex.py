"""
 File: door example 
 Author: I Putu Pawesi Siantika, S.T.
 Date: July 2023

 This file is intended for give an example of how to
 operate door driver.

 prerequisites:
    packages:
        wiringpi: accessing orange-pi-board GPIO hardware
    
"""
import os
import platform
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/door'))

"""
    This is for mocking the GPIO in native device.
    Auto detect the platform and chose correct libraries.
"""
if platform.machine() == "armv7l":
    import wiringpi 
    from wiringpi import GPIO
    
else:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(os.path.join(parent_dir, 'drivers/mock_wiringpi'))
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()
# GpioDoor is for access the door and GpioType is for providing gpio operatio types
from door import GpioDoor, GpioType
# Pins for configuring door lock and door sense
# Both should be digital pins
PIN_DOOR_LOCK = 4
PIN_SENSE_DOOR = 5
# Create an door that uses gpio protocol object.
# The door-lock actuator operates in active high type.
door = GpioDoor(PIN_DOOR_LOCK, PIN_SENSE_DOOR, GpioType.ACTIVE_HIGH)
# lock the door
door.lock() 
# Unlock the door
door.unlock()
# Shows the state of door in digital data.
# it returns 0 or 1, we have to decide the return value
# When it represents openned door or closed door.
print(door.sense_door_state()) 
