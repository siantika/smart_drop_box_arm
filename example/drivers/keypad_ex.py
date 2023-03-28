import platform
import sys
sys.path.append('drivers/keypad')

if platform.machine() == 'armv7l':
    import wiringpi 
    from wiringpi import GPIO
    
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()

from keypad import Keypad

keypad = Keypad()

print("please touch the keypad once (single char)")
while True:
    read_input_char = keypad.reading_input_char()
    print(read_input_char)