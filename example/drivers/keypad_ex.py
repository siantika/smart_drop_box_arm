"""
    File: Keypad Example
    Author: I Putu Pawesi Siantika, S.T.
    Date: July 2023

    This file is intended for give an example about how
    to use keypad driver (uart keypad driver).

    Prerequisites:
        Packages:
            * pySerial -> serial communication used between SBC
                          and keypad.
"""
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
# Import keypad driver
from keypad import KeypadMatrixUart
# Create an keypad object that uses uart protocol
keypad = KeypadMatrixUart('/dev/ttySerial0', 9600)

print("Please press the keypad matrix once (single char)!")
print(" Text:")
while True:
    # Read single char from keypad and print it if it is exist.
    char_data = keypad.reading_input_char()
    if char_data is not None: print(char_data)