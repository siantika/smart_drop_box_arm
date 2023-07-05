""" 
Module: lcd driver
author: I Putu Pawesi Siantika, S.T.
date  : Feb 2023. Refactored in July 2023

This module performs basic LCD 16 x 2 operations. It can write lcd using
embedded protocols.

Classes:
- LowLevelIternface : Common interface of low level programming LCD (byte manipulations)
- I2CPCF8574: Implementation of LowLevelInterface using I2C protocol.
- LcdInterface: Common interface of LCD driver.
- LcdI2C :Implemntation of LCD driver using I2C low level programming. 

 From datasheet of LCD 16 x 2 and i2c pcf8574.
    LCD 16 x 2: https://www.sparkfun.com/datasheets/LCD/ADM1602K-NSW-FBS-3.3v.pdf.
    pcf8574   : https://www.nxp.com/docs/en/data-sheet/PCF8574_PCF8574A.pdf 
"""

import time
from abc import ABC, abstractmethod
from smbus2 import SMBus


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


class LowLevelInterface(ABC):
    """
        Represents a low-level interface (protocol data) for accessing LCD registers.
        Specifically designed for the I2C protocol.
    """
    @abstractmethod
    def _write_byte_data(self, byte_data)->None:
        """ Writes a single bit to LCD register"""
        pass

    @abstractmethod
    def _latch_en_pin(self, byte_data)->None:
        """ Generates pulse for enable pin in LCD hardware"""
        pass

    @abstractmethod
    def _send_data_to_reg(self, data)->None:
        """ Transmits data from SBC to LCD 16 x 2 in one cycle. """
        pass

    @abstractmethod
    def _set_mode_in_4_bit(self)->None:
        """Sets the LCD hadware in 4 bit mode"""
        pass

    @abstractmethod
    def _send_data_4_bit(self, data_lcd, mode)->None:
        """ Sends 4 bit data for higer and low register (8 bit) """
        pass


class I2CPCF8574(LowLevelInterface):
    """ Implementation for I2C PCF8574 module
        It refers to datasheet put above ! """
    def __init__(self, dev_addr, bus_line:int) -> None:
        """ 
            Constructs I2C communcation between SBC and I2C module.
                Args:
                    dev_addr (hex): PCF8574 address.
                    bus_line (int): The line used for performing I2C communication.
        """
        self._dev_addr = int(dev_addr)
        self._bus_line = int(bus_line)
        self.bus = SMBus()
        self.bus.open(self._bus_line) 

    def _write_byte_data(self, byte_data)->None:
        """ 
            Writes a byte to register of LCD 16 x 2 hardware.
            Args:
                byte_data (hex): a byte transferred to LCD register.
        """
        self.bus.write_byte(self._dev_addr, int(byte_data))
        time.sleep(0.0001)
    
    def _latch_en_pin(self, byte_data) -> None:
        """ 
            Latches and transfer byte data to LCD hardware according to LCD datasheet.
            It also turn the backlight bit on. 
                Args:
                    byte_data (hex) : a byte transferred to LCD hardware in
                                      one cycle.
        """
        self._write_byte_data(byte_data | EN_PIN | BACKLIGHT_ON)
        time.sleep(0.0005)
        self._write_byte_data((byte_data & ~EN_PIN) | BACKLIGHT_ON )
        time.sleep(0.001)
    
    def _send_data_to_reg(self, data) -> None:
        """ Steps for sending data to LCD register according LCD datasheet"""
        self._write_byte_data(data | BACKLIGHT_ON)
        self._latch_en_pin(data)

    def _set_mode_in_4_bit(self) -> None:
        """ Since we use I2C PCF8574, we only can send 4 bits data from 8 bit in total,
        So we set 4 bits data transfer for 8 bits availble bit in a register. """
        self._send_data_to_reg(MODE_4_BIT | TWO_LINE_BIT)
    
    def _send_data_4_bit(self, data_lcd, mode:int) -> None:
        """ 
            Since we use I2C PCF8574, we only can send 4 bits data from 8 bit in total,
            So we send 4 bits first for higer register then we send another 4 bits for lower bit register.
                Args:
                    data_lcd(hex) : 4 bits data to be transferred.
                    mode (int)    : MODE_SETUP_LCD and MODE_WRITE_LCD (datasheet LCD)
                Raises:
                    ValueError: When mode is set outside 0, 1.
        """
        if mode in [MODE_SETUP_LCD, MODE_WRITE_LCD]:
            self._send_data_to_reg((data_lcd & 0xF0) | mode) ### higer order
            self._send_data_to_reg(((data_lcd & 0x0F) << 4) | mode) ### lower order
        else:
            raise ValueError("mode should be between [0,1]")


class LcdInterface(ABC):
    """ High level interface for LCD driver"""
    @abstractmethod
    def clear_lcd(self)->None:
        """ Clears LCD display"""
        pass

    @abstractmethod
    def return_home(self) -> None:
        """ Returns cursor to intial condition (start of pixel)"""
        pass

    @abstractmethod
    def set_display_control_default(self) -> None:
        """ Sets a control display for LCD """
        pass

    @abstractmethod
    def write_text(self, line:int, text:str) -> None:
        """ Displays the text according to lines (vertical pos)"""
        pass

    @abstractmethod
    def init_lcd(self)-> None:
        """ Prepares LCD to display first text"""
        pass


class LcdI2C(LcdInterface):
    """
        Implementation of LCD using I2C protocol communication (pcf 8574)
    """
    def __init__(self, dev_addr, bus_line) -> None:
        """ 
            Initialize LCD object for I2C LCD.
                Args:
                    dev_addr (hex) : Device address of I2C PCF8574.
                    bus_line       : Bus line used in I2C communication.
        """
        self.low_level = I2CPCF8574(dev_addr, bus_line)

    def clear_lcd(self) -> None:
        """ Clears all texts on LCD display"""
        self.low_level._send_data_4_bit(CLEAR_LCD_CMD,MODE_SETUP_LCD)

    def return_home(self) -> None:
        """ Returns cursor to initial condition(first pixel)"""
        self.low_level._send_data_4_bit(RETURN_HOME_CMD, MODE_SETUP_LCD) 

    def set_display_control_default(self) -> None:
        """ Sets display control using I2C protocol especially PCF8574 module """
        self.low_level._send_data_4_bit(DISPLAY_CONTROL_INITIAL | SET_DISPLAY_CONTROL_NO_CURSOR | SET_DISPLAY_CONTROL_NO_CURSOR_BLINKING | SET_DISPLAY_CONTROL_ON, MODE_SETUP_LCD)

    def write_text(self, line:int, text:str)-> None:
        """ 
            Displays text in a line 
                Args:
                    line (int) : Start of vertical position in LCD [0,1]
                    text (str) : Text to be displayed. Max is 16 chars.
                Raises:
                    ValueError for inserting line outside 0 and 1 in line arg. 
                    We only use 16 x 2 LCD.
                    ValueError for inserting more that 16 chars in text arg.
        """
        if line in [0,1] and len(text) <= 16:
            if line == 0:
                self.low_level._send_data_4_bit(SET_LCD_POS_0, MODE_SETUP_LCD)
            elif line == 1:
                self.low_level._send_data_4_bit(SET_LCD_POS_1, MODE_SETUP_LCD)            
            # Display the text in LCD.
            # built-in method: ord --> convert char to unicode-8(utf)
            for char in text:
                self.low_level._send_data_4_bit(ord(char), MODE_WRITE_LCD)

        elif line not in [0,1]:
            raise ValueError('line should not exceed 1')
        elif len(text) > 16:
            raise ValueError("text's length exceeded 16 chars!")

    def init_lcd(self)-> None:
        '''
            Don't change the hierrachy of methods!
            NOTE: After tested so many times, I found the "set 4 byte mode"method
                occured an error in LCD display (When we run the program twice or repeats
                in even, it displays weird characters!). So I removed it.
        '''
        time.sleep(0.0005)
        self.set_display_control_default()
        self.clear_lcd()
        self.return_home()
    