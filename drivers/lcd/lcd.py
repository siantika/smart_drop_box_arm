'''
    File           : lcd.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
    The minimal command to use LCD 16 x 2 with i2c pcf8574.
    . Please find the address of i2c and the bus ( you can use i2c-tools package in linux)
    see test_lcd.py for full documentation!

    * Prerequisites *
    1. SMBus2 lib.
    2. Download or put this library in your working directory project.
    3. Import it to your project file (eg. main.py)

    Example code:
        see: './example/lcd_ex.py' file!

    License: see 'licenses.txt' file in the root of project
'''

from smbus2 import SMBus
import time

EN_PIN = 0x04
MODE_4_BIT = 0x20
TWO_LINE_BIT = 0x08

MODE_SETUP_LCD = 0x00
MODE_WRITE_LCD = 0x01

BACKLIGHT_ON = 0x08

CLEAR_LCD_CMD = 0x01
RETURN_HOME_CMD = 0x02
DISPLAY_CONTROL_INITIAL = 0x08
SET_DISPLAY_CONTROL_ON = 0x04
SET_DISPLAY_CONTROL_NO_CURSOR = 0x00
SET_DISPLAY_CONTROL_NO_CURSOR_BLINKING = 0x00
SET_LCD_POS_0 = 0x80
SET_LCD_POS_1 = 0xC0

class Lcd:
   
    def __init__(self, dev_addr, bus_line):
        self._dev_addr = int(dev_addr)
        self._bus_line = int(bus_line)
        self.bus = SMBus()
        self.bus.open(self._bus_line) 

    ### low level methods and private
    def _write_byte_data(self, byte_data):
        self.bus.write_byte(self._dev_addr, int(byte_data))
        time.sleep(0.0001)
    
    def _latch_en_pin(self, byte_data):
        self._write_byte_data(byte_data | EN_PIN | BACKLIGHT_ON)
        time.sleep(0.0005)
        self._write_byte_data((byte_data & ~EN_PIN) | BACKLIGHT_ON )
        time.sleep(0.001)
    
    def _send_data_to_reg(self, data):
        self._write_byte_data(data | BACKLIGHT_ON)
        self._latch_en_pin(data)

    def _set_mode_in_4_bit(self):
        self._send_data_to_reg(MODE_4_BIT | TWO_LINE_BIT)
    
    def _send_data_4_bit(self, data_lcd, mode):
        self._mode = mode
        if self._mode in [MODE_SETUP_LCD, MODE_WRITE_LCD]:
            self._send_data_to_reg((data_lcd & 0xF0) | self._mode) ### higer order
            self._send_data_to_reg(((data_lcd & 0x0F) << 4) | self._mode) ### lower order
        else:
            raise ValueError("mode should be between [0,1]")


### higher methods and public
    def clear_lcd(self):
        self._send_data_4_bit(CLEAR_LCD_CMD,MODE_SETUP_LCD)

    def return_home(self):
        self._send_data_4_bit(RETURN_HOME_CMD, MODE_SETUP_LCD) 

    def set_display_control_default(self):
        self._send_data_4_bit(DISPLAY_CONTROL_INITIAL | SET_DISPLAY_CONTROL_NO_CURSOR | SET_DISPLAY_CONTROL_NO_CURSOR_BLINKING | SET_DISPLAY_CONTROL_ON, MODE_SETUP_LCD)

    def write_text(self, line, text):
        self._line = line
        self._text = str(text)

        if self._line in [0,1] and len(self._text) <= 16:
            if self._line == 0:
                self._send_data_4_bit(SET_LCD_POS_0, MODE_SETUP_LCD)
            
            elif self._line == 1:
                self._send_data_4_bit(SET_LCD_POS_1, MODE_SETUP_LCD)
            
            ### display text in LCD.
            ### built-in method: ord --> convert char to unicode-8(utf)
            for c in self._text:
                self._send_data_4_bit(ord(c), MODE_WRITE_LCD)

        elif self._line not in [0,1]:
            raise ValueError('line should not exceed 1')
        elif len(self._text) > 16:
            raise ValueError("text's length exceeded 16 chars!")

    def init_lcd(self):
        '''
            Don't change the hierrachy of methods!
        '''
        time.sleep(0.5)
        self._set_mode_in_4_bit()
        self.set_display_control_default()
        self.clear_lcd()
        self.return_home()
        time.sleep(0.2)
       

    