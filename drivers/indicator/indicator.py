'''
    File           : indicator.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
    Indicator driver to run simple LED or GPIO (HIGH/LOW). It can turn on, turn off, and
    read the state of indicator's pin.

    NOTE:
        If it is intended to be ran on Orange Pi board, you should put " --hw-orpi " argument
        when you try to run the program. eg: "python3 ./main.py --hw-orpi "

    License: see 'licenses.txt' file in the root of project
'''

import sys
if sys.argv == '--hw-orpi':
    import mock_wiringpi
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class Indicator:
    def __init__(self, pin):
        self._pin = pin
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self._pin, GPIO.OUTPUT)
        wiringpi.digitalWrite(self._pin, GPIO.LOW)

    def turn_on(self):
        wiringpi.digitalWrite(self._pin, GPIO.HIGH)

    def turn_off(self):
        wiringpi.digitalWrite(self._pin, GPIO.LOW)
        
    def read_state(self):
        return wiringpi.digitalRead(self._pin)