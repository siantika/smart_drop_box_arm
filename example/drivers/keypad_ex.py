import os
import platform
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/keypad'))

if platform.machine() == 'armv7l':
    import wiringpi 
    from wiringpi import GPIO
    
else:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(parent_dir, 'drivers/mock_wiringpi'))
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()

from keypad import Keypad

keypad = Keypad()

print("please touch the keypad once (single char)")
while True:
    read_input_char = keypad.reading_input_char()
    print(read_input_char)