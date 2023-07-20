"""
Unit tests for Gpio and GpioDoor classes.

The tests cover the initialization, setup, and various methods of the Gpio and GpioDoor classes, which are responsible for setting up and controlling a GPIO door system.

The tests ensure that the classes handle initialization, attribute assignments, method invocations, and expected behavior correctly.

The Gpio class is responsible for initializing the GPIO door setup, while the GpioDoor class provides methods for locking, unlocking, and sensing the state of the door.

The Helper class provides helper methods for mocking the necessary dependencies using the unittest.mock.patch functionality. It sets up patches for the mock_wiringpi module, which is used for emulating the wiringPi library.

The tests are organized into TestGpio and TestGpioDoor classes, each containing multiple test methods that validate different aspects of the corresponding class.

Note: The tests assume the presence of specific constants and dependencies, such as DOOR_PIN, SENSE_PIN, HIGH, LOW, and the door.py module. Make sure the required environment and dependencies are properly set up before running the tests.
"""

from unittest.mock import patch, call
import sys
import pytest
import os 

abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(abs_path, 'drivers/door'))
sys.path.append('drivers/mock_wiringpi')

from door import *

# Constants for testing the hardware
DOOR_PIN  = 2
SENSE_PIN = 3
HIGH = 1
LOW = 0


class Helper:
    def mock_wiringpi_methods(self):
        self.patcher1 = patch('mock_wiringpi.MockWiringPi.wiringPiSetup')
        self.patcher2 = patch('mock_wiringpi.MockWiringPi.pinMode')
        self.patcher3 = patch('mock_wiringpi.MockWiringPi.digitalRead')
        self.patcher4 = patch('mock_wiringpi.MockWiringPi.digitalWrite')
        self.patcher5 = patch('mock_wiringpi.MockWiringPi.pullUpDnControl')

        self.mock_wiringpi_wiringPiSetup = self.patcher1.start()
        self.mock_wiringpi_pinMode = self.patcher2.start()
        self.mock_wiringpi_digitalRead = self.patcher3.start()
        self.mock_wiringpi_digitalWrite = self.patcher4.start()
        self.mock_wiringpi_pullUpDnControl = self.patcher5.start()

    def tear_down(self):
        patch.stopall()


class TestGpio(Helper):
    def test_init_should_handle_correctly(self):
        gpio_setup = Gpio(DOOR_PIN, SENSE_PIN)
        assert gpio_setup._door_pin == 2
        assert gpio_setup._sense_door == 3

    def test_init_should_handle_wrong_value_correctly(self):
        with pytest.raises(ValueError):
            gpio_setup = Gpio('GPIO_5', 'GPIO_12')

    def test_gpio_setup_should_invoke_methods_correctly(self):
        self.mock_wiringpi_methods()
        gpio_setup = Gpio(DOOR_PIN, SENSE_PIN)
        gpio_setup.setup()
        self.mock_wiringpi_wiringPiSetup.assert_called_once()
        self.mock_wiringpi_pinMode.assert_has_calls(
            [
                call(2, 1),
                call(3, 0),
            ]
        )
        self.mock_wiringpi_pullUpDnControl.assert_called_once_with(
            3, GPIO.PUD_UP
        )
        self.tear_down()

class TestGpioDoor(Helper):
    def test_init_should_has_correct_attributes(self):
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_LOW)
        assert isinstance(gpio_door._gpio, Gpio)
        gpio_door.lock()

    def test_with_active_low_door_should_lock(self):
        self.mock_wiringpi_methods()
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_LOW)
        gpio_door.lock()
        self.mock_wiringpi_digitalWrite.assert_called_with(DOOR_PIN, 0)
        self.tear_down()

    def test_door_lock_with_(self):
        self.mock_wiringpi_methods()
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_HIGH)
        gpio_door.lock()
        self.mock_wiringpi_digitalWrite.assert_called_with(DOOR_PIN, 1)
        self.tear_down()
    
    def test_unlock_door_with_active_high(self):
        self.mock_wiringpi_methods()
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_HIGH)
        gpio_door.unlock()
        self.mock_wiringpi_digitalWrite.assert_called_with(2, 0)
        self.tear_down()

    def test_unlock_door_with_active_low(self):
        self.mock_wiringpi_methods()
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_LOW)
        gpio_door.unlock()
        self.mock_wiringpi_digitalWrite.assert_called_with(2, 1)
        self.tear_down()
    
    def test_door_door_state_should_return_high_when_door_is_open(self):
        self.mock_wiringpi_methods()
        self.mock_wiringpi_digitalRead.return_value = HIGH
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_LOW)
        state = gpio_door.sense_door_state()
        self.mock_wiringpi_digitalRead.assert_called_with(3)
        assert state == 1
        self.tear_down()
        
    def test_door_door_state_should_return_high_when_door_is_open(self):
        self.mock_wiringpi_methods()
        self.mock_wiringpi_digitalRead.return_value = LOW
        gpio_door = GpioDoor(DOOR_PIN, SENSE_PIN, GpioType.ACTIVE_LOW)
        state = gpio_door.sense_door_state()
        self.mock_wiringpi_digitalRead.assert_called_once_with(3)
        assert state == 0
        self.tear_down()
