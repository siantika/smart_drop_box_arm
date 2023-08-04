"""
Module: door driver
author: I Putu Pawesi Siantika, S.T.
date  : Feb 2023. Refactored in July 2023.

This module provides classes for acessing door functions.
Door hardware in custom hardware. It is composed from
door-lock actuator and door-sense sensor (digital data)

Classes:
 - DoorInterface: Common interface for Door
 - GpioTyoe : Class Constants for specifying gpio active type.
 - HardwareProtocol: Common interface for Hardware protocol acessing
                     door hardwares.
 - Gpio (inherits HardwareProtocol): Implementation for acessing door using GPIO
 - GpioDoor (inherits DoorInterface):Implementation for door functional 
   (lock, unlok, and sense)
"""
import sys
import os 
import platform
from abc import ABC, abstractmethod

if platform.machine() == "armv7l":
    import wiringpi 
    from wiringpi import GPIO
    
else:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.append(os.path.join(parent_dir, 'src/drivers/mock_wiringpi'))
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class DoorInterface(ABC):
    """ Common interface for Door Interface"""
    @abstractmethod
    def lock(self):
        """ Locks the door """
        pass 

    @abstractmethod
    def unlock(self):
        """ Unlock the door """
        pass

    @abstractmethod
    def sense_door_state(self):
        """ Senses door state"""
        pass 

class HardwareProtocol(ABC):
    """ Interface for hardware protocol. It can be i2c, spi, etc"""
    @abstractmethod
    def setup(self):
        """ Setup hardware protocol"""
        pass 


class GpioType:
    """ Stores class variables for Gpio operation type """
    ACTIVE_HIGH = 1
    ACTIVE_LOW = 0


class Gpio(HardwareProtocol):
    """ Implementation of hardware protocol interface using GPIO """
    def __init__(self, door_pin:int, sense_pin:int) -> None:
        """ Construct an Gpio protocol object 
            Args:
                door_pin (int) : pin of the door lock
                sense_pin (int) : pin of door-sense sensor
            Raises:
                ValueError : If door pin or sense_pin are inputted
                with wrong data type (not int).
        """
        if not isinstance(door_pin, int) or not isinstance(sense_pin, int):
            raise ValueError("pins should be interger type!")
        self._door_pin = door_pin
        self._sense_door = sense_pin

    def setup(self):
        """ Setup a GPIO protocol for accessing door hardware """
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self._door_pin, GPIO.OUTPUT)
        wiringpi.pinMode(self._sense_door, GPIO.INPUT)
        wiringpi.pullUpDnControl(self._sense_door, GPIO.PUD_UP)
        

class GpioDoor(DoorInterface):
    """ Implementation of DoorInterface interface using GPIO protocol """
    def __init__(self, door_pin:int, sense_pin:int, door_active_type:GpioType):
        """ Construct a Gpio door object 
            Args:
                door_pin (int) : digital pin for door-lock actuator
                sense_pin (int) : digital pin for door-sense sensor
                door_active_type (GpioType) : state of gpio which marks
                if door-lock actuator is ON. GpioType.ACTIVE_HIGH means
                the door-lock actuator will be on if we set the GPIO level
                in that hardware HIGH or 1 and vice versa. 
        """
        self._gpio = Gpio(door_pin, sense_pin)
        self._turn_on = None 
        self._turn_off = None
        # Factory for gpio type operation.
        if door_active_type is GpioType.ACTIVE_HIGH:
            self._turn_on = GPIO.HIGH
            self._turn_off = GPIO.LOW
        else:
            self._turn_on = GPIO.LOW
            self._turn_off = GPIO.HIGH
        self.lock() 

    def lock(self):
        """ Lock the door using GPIO protocol """
        wiringpi.digitalWrite(self._gpio._door_pin, self._turn_on)

    def unlock(self):
        """ Unlock the door using GPIO protocol """
        wiringpi.digitalWrite(self._gpio._door_pin, self._turn_off)

    def sense_door_state(self):
        """ Sense the door's state using GPIO protocol """
        return wiringpi.digitalRead(self._gpio._sense_door)
    