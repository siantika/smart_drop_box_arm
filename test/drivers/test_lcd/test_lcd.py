""" 
Test cases for LCD interface. I tests I2C PCF8574
implementation for LowLevelInterface and LCDi2C driver implementation.

"""
import os
import sys
import time
from smbus2 import SMBus
from unittest.mock import patch, call
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'src/drivers/lcd'))
from lcd import *

test_dev_addr = 0x27
test_bus_line_0 = 0
test_bus_line_1 = 1
test_data_byte_sent = 0x20
test_mode_set_config = 0
test_mode_set_write_data = 1

BACKLIGHT_ON = 0x08

'''
   The test performs in arch PC. We mock all the arm dependencies.
   I tested on orange pi zero that runs armbian.
'''
class HelperGeneral:
    def set_up(self):
        self.patcher = patch('smbus2.SMBus.open')
        self.mock_SMBus_open = self.patcher.start()
        self.mock_SMBus_open.return_value(None)
        # Lower level object
        self.low_level = I2CPCF8574(test_dev_addr, test_bus_line_0)
        # High level object
        self.lcd = LcdI2C(test_dev_addr, test_bus_line_0)

    def help_mock__send_data_to_reg(self):
        self.patcher1 = patch('smbus2.SMBus.write_byte')
        self.patcher2 = patch('time.sleep')
        
        # Mock the low level methods
        self.patcher3 = patch('lcd.I2CPCF8574._write_byte_data')
        self.patcher4 = patch('lcd.I2CPCF8574._latch_en_pin')
        self.patcher5 = patch('lcd.I2CPCF8574._send_data_to_reg')

        self.mock_write_byte = self.patcher1.start()
        self.mock_sleep = self.patcher2.start()
        self.mock__write_byte_data = self.patcher3.start()
        self.mock_latch_en = self.patcher4.start()
        self.mock__send_data_to_reg = self.patcher5.start()

    def help_mock_send_4_bits_data(self):
        self.patcher_send_4_bit = patch('lcd.I2CPCF8574._send_data_4_bit')
        self.mock__send_data_4_bit = self.patcher_send_4_bit.start()

    def tear_down(self):
        patch.stopall()


class TestConstructorOfLowLevelPCF8574(HelperGeneral):
    '''
        Test the constructor of class. It should instantiate SMBus lib 
        (I2C Protocol lib in python3) correctly.
    '''
    def test_init_process_device_addres_shouldbe_an_integer(self):
        self.set_up()
        assert isinstance(self.low_level._dev_addr, int)
        self.tear_down()

    def test_init_process_bus_line_shouldbe_an_integer(self):
        self.set_up()
        assert isinstance(self.low_level._bus_line, int)
        self.tear_down()

    def test_init_process_should_initiate_smbus_object(self):
        self.set_up()
        assert isinstance(self.low_level.bus, SMBus) == True
        self.tear_down()

    def test_init_process_bus_should_open_correct_bus_line_0(self):
        '''
            Called the bus 0
        '''
        self.patcher = patch('smbus2.SMBus.open')
        self.mock_SMBus_open = self.patcher.start()
        self.mock_SMBus_open.return_value(None)
        self.low_level = I2CPCF8574(test_dev_addr, test_bus_line_0)
        self.mock_SMBus_open.assert_called_once_with(0)
        self.tear_down()

    def test_init_process_bus_should_open_correct_bus_line_1(self):
        '''
            Called the bus 1
        '''
        self.patcher = patch('smbus2.SMBus.open')
        self.mock_SMBus_open = self.patcher.start()
        self.mock_SMBus_open.return_value(None)
        self.low_level = I2CPCF8574(test_dev_addr, test_bus_line_1)
        self.mock_SMBus_open.assert_called_once_with(1)
        self.tear_down()


class TestI2CPCF8574Method(HelperGeneral):
    '''
        Test private methods in Low Level interface.
    '''
    @patch('time.sleep')
    def test_write_data_byte_should_sent_correct_data(self, mock_time_sleep):
        with patch('smbus2.SMBus.write_byte') as mock_write_byte:
            self.set_up()
            self.low_level._write_byte_data(0x20)
            mock_write_byte.assert_called_once_with(int(test_dev_addr), int(test_data_byte_sent))
            mock_time_sleep.assert_has_calls([
            call(0.0001),
            ])
         
    @patch('time.sleep')
    @patch('smbus2.SMBus.write_byte')
    def test_latch_low_bit_assigned_shouldbe_executed_correctly(self, mock_write_byte, mock_time_sleep):
        '''
            execute the delay respectively.
            this refers to datasheet in https://www.sparkfun.com/datasheets/LCD/ADM1602K-NSW-FBS-3.3v.pdf (P.7).
        '''
        self.set_up()
        self.low_level._latch_en_pin(0x01)     ### data = 0x01

        mock_write_byte.assert_has_calls([
            call(0x27, 0x0D), ### data 0x01 | EN pin (0x04)| backlight on (0x08)
            call(0x27, 0x09), ## OR with backlight ON
        ])

        mock_time_sleep.assert_has_calls([
            call(0.0005),
            call(0.0001),
            call(0.001) ### for after latch delay!
        ])

    @patch('time.sleep')
    @patch('smbus2.SMBus.write_byte')
    def test_latch_high_bit_assigned_shouldbe_executed_correctly(self, mock_write_byte, mock_time_sleep):
        '''
            execute delay respectively with correct time delay (according datasheet).
            this refers to datasheet in https://www.sparkfun.com/datasheets/LCD/ADM1602K-NSW-FBS-3.3v.pdf (p.7)
        '''
        self.set_up()
        self.low_level._latch_en_pin(0xF0)    

        mock_write_byte.assert_has_calls([
            call(0x27, 0xF4 | BACKLIGHT_ON), ### or with BACKLIGHT (enable)
            call(0x27, 0xF0 | BACKLIGHT_ON), ### or with BACKLIGHT (enable)
        ])

        mock_time_sleep.assert_has_calls([
            call(0.0005),
            call(0.0001),
        ])

    @patch('time.sleep')
    @patch('smbus2.SMBus.write_byte')
    @patch('lcd.I2CPCF8574._write_byte_data')
    @patch('lcd.I2CPCF8574._latch_en_pin')
    def test_data_shouldbe_sent_correctly(self, mock__latch_en_pin,mock__write_byte_data, mock_write_byte, mock_time_sleep,):
        self.set_up()
        self.low_level._send_data_to_reg(0xAA | BACKLIGHT_ON) ### backlight LCD on
        mock__write_byte_data.assert_called_once_with(0xAA)
        mock__latch_en_pin.assert_called()


    def test_set_function_in_4_mode_should_be_correct(self):
        '''
            data to be sent to set 4 bit mode: 0b0010 0000 (msb -> lsb) or 20h in i2c pcf8574 pins so that
             p7 p6 p5 p4 p3 p2  p1  p0  (pcf8574's pins)
             D7 D6 D5 D4 X  E  R/W RS   (lcd 16x2's pins) 
            this refer to datasheet in https://www.sparkfun.com/datasheets/LCD/ADM1602K-NSW-FBS-3.3v.pdf (p.11-p.12) and
            pcf8574's datasheet: https://www.nxp.com/docs/en/data-sheet/PCF8574_PCF8574A.pdf (p.8)
        '''
        self.set_up()

        self.help_mock__send_data_to_reg()
        self.low_level._set_mode_in_4_bit() ### 4 mode , 2 lines, 5x8 dots (lcd dasatasheet p.11)
        self.mock__send_data_to_reg.assert_called_once_with(0x28)

        self.tear_down()


    def test__send_data_4_bit_mode_should_choose_correct_mode_parameters(self):
        self.set_up()
        self.help_mock__send_data_to_reg()

        ## should be raise an error message
        try:
            self.low_level._send_data_4_bit(0x20, 2) 
        except ValueError as ve:
            assert str(ve) == "mode should be between [0,1]"
        else:
            assert False

        self.tear_down()

    def test__send_data_4_bit_mode_should_be_correct(self):
        '''
            to control lcd 16 x 2 in 4 bit mode command, we have to convert 8-bit data (D7-D0 in lcd's pins) to 
            4 bit data. eg.
                0b0011 0101 (8-bit) 
            to 
                0b0011 (4-bit higher)
            send it
                0b0101 (4-bit lower)
            send it  
            .. it has mode parameter to control the mode (setup or write data) only 0 = setup and 1 = write
        '''
        self.set_up()
        self.help_mock__send_data_to_reg()

        self.low_level._send_data_4_bit(0x35, 0)
        
        self.mock__send_data_to_reg.assert_has_calls(
            [
                call(0x30),
                call(0x50)
            ]
        )
        self.tear_down()


    def test__send_data_4_bit_for_control_bit_should_be_correct(self):
        '''
            control bits located in low order bits (pcf8574), there are R/W , En, and RS. normally, EN is 0.
            eg. 0b1110 0011 --> low order bits (especially last 2 bits is control bit). we should combine data 
            to be sent (higher 4 order bit) and control bit.
        '''
        self.set_up()
        self.help_mock__send_data_to_reg()

        self.low_level._send_data_4_bit(0x03, test_mode_set_config) 
        self.low_level._send_data_4_bit(0xE2, test_mode_set_write_data)

        self.mock__send_data_to_reg.assert_has_calls(
            [
                call(0x00),
                call(0x30),
                call(0xE1),
                call(0x21)
            ]
        )
        self.tear_down()



class TestLcdI2C(HelperGeneral):
    '''
        Test High level LCD abstraction
    '''
    
    def test_lcd_should_execute_clear_lcd_method_correctly(self):
        self.set_up()
        self.help_mock__send_data_to_reg()
        self.help_mock_send_4_bits_data()

        self.lcd.clear_lcd()

        self.mock__send_data_4_bit.assert_called_once_with(0x01, 0x00) ### data: 0b0000 0001 || setup command
        self.tear_down()

    def test_lcd_should_execute_return_home_method_correctly(self):
        self.set_up()
        self.help_mock__send_data_to_reg()
        self.help_mock_send_4_bits_data()

        self.lcd.return_home()

        self.mock__send_data_4_bit.assert_called_once_with(0x02, 0x00) ### data: 0b0000 002x || setup command

        self.tear_down()

    def test_set_display_control_shouldbe_correct(self):
        '''
            set the control display to display on, cursor off, and cursosr blink is off, 
        '''
        self.set_up()
        self.help_mock__send_data_to_reg()
        self.help_mock_send_4_bits_data()

        self.lcd.set_display_control_default()

        self.mock__send_data_4_bit.assert_called_once_with(0x0C, 0x00) ### data: 0b0000 1100 || setup command

        self.tear_down()


    def test_write_text_should_has_correct_parameters(self):
        '''
            Set line and pos for writing char. This is 2 line lcd, so the start of fisrt line address start bewtween 00h to 27h
            second line should be between 40h to 67h(d6-d0)
           . Dont forget to | data with the initial bit for set address. eg 0b1xxx xxxx (x -> bit adress)
        '''
        self.set_up()
        self.help_mock__send_data_to_reg()
        self.help_mock_send_4_bits_data()

        self.lcd.write_text(0, 'sian')
        ### line should showing Value Error if inserted outside [0,1]
        try:
            self.lcd.write_text(5, 'sian')
        except ValueError as ve:
            assert str(ve) == 'line should not exceed 1'
        else:
            assert False

        ### text exceeds 16 chars should raise a ValueError
        try:
            self.lcd.write_text(0, 'dsfsdfsdfsdfsdf4544545454545454445454545454531545454')
        except ValueError as ve:
            assert str(ve) == "text's length exceeded 16 chars!"
        else:
            assert False
        self.tear_down()

    def test_write_text_should_execute_correctly_in_line_0(self):
        self.set_up()
        self.help_mock__send_data_to_reg()
        self.help_mock_send_4_bits_data()

        ### write in line 0 and check convertion to unicode for text
        self.lcd.write_text(0, "sian")
        self.mock__send_data_4_bit.assert_has_calls(
            [
                call(0x80, 0x00), ### setup MODE = 0
                ### send text in unicode --> sian = 73 69 61 6E (write mode)
                call(0x73, 0x01),
                call(0x69, 0x01),
                call(0x61, 0x01),
                call(0x6E, 0x01),
            ]
        )
        self.tear_down()

    def test_write_text_should_execute_correctly_in_line_1(self):
        self.set_up()
        self.help_mock__send_data_to_reg()
        self.help_mock_send_4_bits_data()

         ### write in line 1 check convertion to unicode for text
        self.lcd.write_text(1,"25si90'!") ### text's unicode = 32 35 73 69 39 30 27 21
        self.mock__send_data_4_bit.assert_has_calls(
            [
                call(0xC0, 0x00), ### setup MODE = 0
                ### send text in unicode --> sian = 73 69 61 6E (write mode)
                call(0x32, 0x01),
                call(0x35, 0x01),
                call(0x73, 0x01),
                call(0x69, 0x01),
                call(0x39, 0x01),
                call(0x30, 0x01),
                call(0x27, 0x01),
                call(0x21, 0x01),
            ]
        )
        self.tear_down()



class TestInitLcdI2C(HelperGeneral):
    @patch.object(LcdI2C, 'set_display_control_default')
    @patch.object(LcdI2C, 'return_home')
    @patch.object(LcdI2C, 'clear_lcd')    

    def test_init_lcd_should_execute_correctly(self, mock_clear_lcd, mock_return_home, mock_set_display_control_lcd):
        '''
            1. set address
            2. set mode to 4 mode (DELETED, It caused an error)
            3. clear display
            4. return home
            5. set display cursor
            6. delay(0.2) --> from https://github.com/the-raspberry-pi-guy/lcd/blob/master/drivers/i2c_dev.py (line 111)
        '''

        self.set_up()
        self.help_mock__send_data_to_reg()
        self.lcd.init_lcd()
        mock_clear_lcd.assert_called_once()
        mock_return_home.assert_called_once()
        mock_set_display_control_lcd.assert_called_once()
        self.mock_sleep.assert_has_calls(
            [
                call(0.0005),
            ]
        )
        self.tear_down()



        

        



        







        




      