import sys
sys.path.append('drivers/keypad')
import time
if '--hw-orpi' in sys.argv:
    import wiringpi 
    
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()

from keypad import Keypad

### var
PINS_ROW_KEYPAD = [2,3,4,6]
PINS_COLUMN_KEYPAD = [8,11,12,14]

keypad = Keypad(PINS_ROW_KEYPAD, PINS_COLUMN_KEYPAD)

print("please touch the keypad once (single char)")
read_input_char = keypad.reading_input_char()
print(read_input_char)