"""
Module: test_keypad
author: I Putu Pawesi Siantika, S.T.
date  : July 2023

This module performs unit tests for keypad driver.

Classes:
- TestKeypadMatrixUart : Test behaviour of keypad using
                         uart protocol
"""


import sys
import pytest
import serial
sys.path.append('drivers/keypad')
sys.path.append('drivers/mock_wiringpi')

from keypad import *

TEST_SERIAL_PATH = 'dev/ttyS1'
TEST_BAUDRATE = 9600

class TestKeypadMatrixUart:
    """
        Only posible to test the init method. To get comprehensive result,
        we should test directing to hardware level.
    """
    def set_up(self):
        uart_protocol = KeypadProtocolUart('dev/ttyS1', 9600)
        self.keypad = KeypadMatrixUart(uart_protocol)
    
    def test_init_should_inisiate_keypadprotocoluart_class(self):
        self.set_up()
        isinstance(self.keypad._communication, KeypadProtocolUart)


class TestKeypadProtocolUart:
    def set_up(self):
        self.uart_protocol = KeypadProtocolUart(
            TEST_SERIAL_PATH,
            TEST_BAUDRATE,
        )

    def test_attributes_should_be_correct(self):
        self.set_up()
        hasattr(self.uart_protocol, '_port')
        hasattr(self.uart_protocol, '_baudrate')

    def test_attributes_should_be_handle_correct_input(self):
        self.set_up()
        assert self.uart_protocol._port == TEST_SERIAL_PATH
        assert self.uart_protocol._baudrate == TEST_BAUDRATE


    def test_should_raise_error_when_serial_lib_received_wrong_params(self):
        """ When args are not inputted correctly, it should raise an Serial
            Error (inherited from pySerial class)"""
        
        with pytest.raises(serial.SerialException):
            self.set_up()
            self.uart_protocol.initialize()
        

 