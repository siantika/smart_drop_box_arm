import sys

if '--hw-orpi' in sys.argv:
    import wiringpi 
    
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
        self.lock_door()

    def lock_door(self):
        wiringpi.digitalWrite(self._pin_door_solenoid, GPIO.INPUT)

    def unlock_door(self):
        wiringpi.digitalWrite(self._pin_door_solenoid, GPIO.HIGH)

    def sense_door_state(self):
        return wiringpi.digitalRead(self._pin_sense_door)

    