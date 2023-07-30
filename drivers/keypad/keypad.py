"""
Module: keypad driver
author: I Putu Pawesi Siantika, S.T.
date  : Feb 2023. Refactored in July 2023.

This module provides classes for receiving data from keypad.

Classes:
- KeypadInterface (abstract base class): Defines the common interface for keypad method.
- KeypadUartMatrix (inherits KeypadInterface): Implementation of keypad using keypad matrix with
                                                uart protocol.
- KeypadProtocolInterface (abs): Defines the common interface for keypads protocol.
- KeypadProtocolUart (inherits KeypadProtocolInterface): Implementation of keypad protocol using
  uart protocol.

"""
import os
import sys
import platform
from abc import ABC,abstractmethod
import serial
from pathlib import Path

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/mock_wiringpi'))

if platform.machine() == 'armv7l':
    import wiringpi 
    from wiringpi import GPIO
else:
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class KeypadInterface(ABC):
    """ Interface for Keypad"""
    @abstractmethod
    def reading_input_char(self)-> str:
        """ Reads an input char by user"""
        pass

class KeypadProtocolInterface(ABC):
    """ Interface for keypad protocol"""
    @abstractmethod
    def initialize(self)-> any:
        """ Initializes a protocol"""
        pass


class KeypadProtocolUart(KeypadProtocolInterface):
    """ 
        Implementation of Uart protocol for acessing keypad.
        Please make sure the keypad supports uart protocol
        and make sure if the baudrate of SBC and keypad should 
        be matched.
    """
    def __init__(self, port:Path, baudrate:int) -> None:
        """
            Constructor of KeypadProtocolUart class. It initialize
            a serial object from pySerial class.
                args:
                    port(Path) : the path where uart used.
                    baudrate (int) : transfer bit rate.    
        """
        self._port = port 
        self._baudrate = baudrate
    
    def initialize(self) -> serial.Serial:
        """
            Initialize uart protocol using serial library.
            The configurable args only: port and baudrate.
                Raises:
                Inherited from pySerial class:
                    ValueError : when input of baudrate out of range.
                    SerialException : when device can't be found or
                                    can't be configured.
        """
        return serial.Serial(
            port = self._port,
            baudrate = self._baudrate,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 1 # secs
            )
        

class KeypadMatrixUart(KeypadInterface):
    """
        Implementation of keypad matrix using uart protocol.
    """
    def __init__(self, port:Path, baudrate:int ):
        keypad_protocol = KeypadProtocolUart(port, baudrate)
        self._keypad = keypad_protocol.initialize()
    
    def reading_input_char(self)-> str:
        '''
            Reading input char from keypad. 
            It uses a serial communication between keypad and SBC.
                Returns:
                    char_data (str): single char from keypad.
        '''
        char_data = None
        try:
            char_data = self._keypad.readline()\
                .decode('utf-8').strip() 
        except UnicodeDecodeError as msg_error:
            print(f"Error keypad: {msg_error}")
        finally:
            if char_data is not None:
                if len(char_data) == 0:   
                    char_data = None
        return char_data
