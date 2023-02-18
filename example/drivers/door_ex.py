import sys
sys.path.append('drivers/door')

if '--hw-orpi' in sys.argv:
    import wiringpi 
    
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()

from door import Door

### var
PIN_DOOR_LOCK = 4
PIN_SENSE_DOOR = 5

door = Door(PIN_DOOR_LOCK, PIN_SENSE_DOOR)

### methods
door.unlock_door() ### pin door lock == HIGH

door.lock_door() ### pin door lock == LOW

print(door.sense_door_state()) ### return 0 or 1
