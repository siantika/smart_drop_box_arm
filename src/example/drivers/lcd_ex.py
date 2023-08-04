"""
    file : lcd example
    author : I Putu Pawesi Siantika, S.T.

    This file is intended to give how to use LCD driver.

    Prerequisites:
        packages:
            'smbus2' -> performs I2C protocol
            'i2cdetect' -> detect i2c hardware address
        driver:
            lcd.py -> driver for accessing LCD hardware.
    
    Note:
        For now, only works for I2C protocol LCD 16x2
"""
import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/lcd'))
from lcd import LcdI2C

# Constants for initiate  a LCD object
''' To find device address, you need to plug
the lcd hardware module (I2C) to your sbc board (orange pi or raspberry pi).
In your sbc board, run CLI then type this command:
   " find in CLI 'i2cdetect -y 1" 
if success it will return device address of i2c hardware attached on
your SBC board.
Note:
    * Command inputted without quotation mark.
    * Please make sure you installed 'i2cdetect' package
      on your SBC board.
    * You can change -y 1 to -y 0
      according your i2c hardware bus.
'''
PIN_DEV_ADDR = 0x27
BUS_I2C_DEV = 0 

# Create an instance of LCD using I2C protocol class
lcd = LcdI2C(PIN_DEV_ADDR, BUS_I2C_DEV)
# Should be called once in initial steps
lcd.init_lcd()
# Display text on LCD.
# args(line ([0,1]), text)
# line 0 = first row of lcd and so on.

lcd.write_text(0, ' Hello Bali ') 
lcd.write_text(1, 'Om Swastyastu')
# make text display readable for huma before next text
time.sleep(2) 
# we have to clear previous text then we write the new text
lcd.clear_lcd()
lcd.write_text(1, 'Om shanti 3x Om')

# End of file (EOF)
