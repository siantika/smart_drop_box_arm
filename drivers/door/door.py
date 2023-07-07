"""
Module: keypad_driver
author: I Putu Pawesi Siantika, S.T.
date  : Feb 2023. Refactored in July 2023.

This module provides classes for acessing door functions

Classes:
 - DoorInterface: Common interface for Door
 - HardwareProtocol: Common interface for Hardware protocol acessing
                     door hardwares.
 - Gpio (inherits HardwareProtocol): Implementation for acessing door using GPIO
 - GpioDoor (inherits DoorInterface):Implementation for door functional (lock, unlok, and sense)
"""
import sys
import os 
import platform
from abc import ABC, abstractmethod

if platform.machine() == "armv7l":
    import wiringpi 
    from wiringpi import GPIO
    
else:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(parent_dir, 'drivers/mock_wiringpi'))
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class DoorInterface(ABC):
    @abstractmethod
    def lock(self):
        pass 

    @abstractmethod
    def unlock(self):
        pass

    @abstractmethod
    def sense_door_state(self):
        pass 

class HardwareProtocol(ABC):
    @abstractmethod
    def setup(self):
        pass 


class Gpio(HardwareProtocol):
    def __init__(self, door_pin:int, sense_pin:int) -> None:
        if not isinstance(door_pin, int) or not isinstance(sense_pin, int):
            raise ValueError("pin/s should be interger type!")
        self._door_pin = door_pin
        self._sense_door = sense_pin

    def setup(self):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self._door_pin, GPIO.OUTPUT)
        wiringpi.pinMode(self._sense_door, GPIO.INPUT)
        wiringpi.pullUpDnControl(self._sense_door, GPIO.PUD_UP)
        

class GpioDoor(DoorInterface):
    def __init__(self, door_pin, sense_pin ):
        self._gpio = Gpio(door_pin, sense_pin)
        self.lock() 

    def lock(self):
        wiringpi.digitalWrite(self._gpio._door_pin, GPIO.LOW)

    def unlock(self):
        wiringpi.digitalWrite(self._gpio._door_pin, GPIO.HIGH)

    def sense_door_state(self):
        return wiringpi.digitalRead(self._gpio._sense_door)
    