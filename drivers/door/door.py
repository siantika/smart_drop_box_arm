'''
    File           : door.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
    This code helps to control or accessing to the door (solenoid_door and sense_state_door)
    . It can unlock the door, lock the door, and sense_state_door (0 or 1). lock the door means
    the PIN is LOW state and unlock the door means pin is HIGH state. For sensing the state of 
    door, we need sensor detects HIGH or LOW (digital data). The design is CLOSE is HIGH and vice versa (depend on hardware). 
    For more information, see 'test_door.py' file!

    * Prerequisites *
    1. wiringOP lib.
    2. Download or put this library in your working directory project.
    3. Import it to your project file (eg. main.py)

    Example code:
        see: './example/door_ex.py' file!

    License: see 'licenses.txt' file in the root of project
'''

import sys
import platform

if platform.machine() == "armv7l":
    import wiringpi 
    from wiringpi import GPIO
    
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class Door:
    def __init__(self, pin_door_lock, pin_sense_door):
        self._pin_door_solenoid = pin_door_lock
        self._pin_sense_door = pin_sense_door
        self._state_of_door = 0

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self._pin_door_solenoid, GPIO.OUTPUT)
        wiringpi.pinMode(self._pin_sense_door, GPIO.INPUT)
        wiringpi.pullUpDnControl(self._pin_sense_door, GPIO.PUD_UP)
        self.lock_door()

    def lock_door(self):
        wiringpi.digitalWrite(self._pin_door_solenoid, GPIO.INPUT)

    def unlock_door(self):
        wiringpi.digitalWrite(self._pin_door_solenoid, GPIO.HIGH)

    def sense_door_state(self):
        return wiringpi.digitalRead(self._pin_sense_door)

    