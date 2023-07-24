import sys
from unittest.mock import patch
import os
import serial

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'applications/peripheral_operations'))
sys.path.append(os.path.join(parent_dir, 'drivers/keypad'))
sys.path.append(os.path.join(parent_dir, 'drivers/weight'))
sys.path.append(os.path.join(parent_dir, 'drivers/door'))
sys.path.append(os.path.join(parent_dir, 'drivers/camera'))
sys.path.append(os.path.join(parent_dir, 'drivers/sound'))
sys.path.append(os.path.join(parent_dir, 'utils'))

config_dir = os.path.join(parent_dir, 'conf/config.ini')
# Should put here due to local DIY libs
from pins_config import PinsConfig
from keypad import KeypadMatrixUart
from door import GpioDoor, GpioType
from weight import HX711Driver
from sound import Aplay
from camera import UsbCamera, UsbCameraSetting, CameraResolution
from peripheral_operations import PeripheralOperations, \
    PeripheralsSetupCreation as SetupPeriph

class MockResources:
    def help_mock(self):
        self._mock_serial = patch('serial.Serial').start()
        self._mock_peripheral_opt = patch('PeripheralOperations').start()
        # self._mock_camera = patch.object(Periph,'camera').start()
        # self._mock_sound = patch.object(Periph,'sound').start()
        # self._mock_weight = patch.object(Periph,'weight').start()
        # self._mock_door = patch.object(Periph,'door').start()
        self._mock_keypad = patch.object(PeripheralOperations,'keypad').start()
        self._mock_keypad.return_value = None

class TestPeripheralsSetupCreation(MockResources):

    def test_camera_setup_should_be_correct(self):
        self.help_mock()
        camera = SetupPeriph.create_camera_setup()
        assert isinstance(camera, UsbCamera)

    def test_sound_setup_should_be_correct(self):
        self.help_mock()
        sound = SetupPeriph.create_sound_setup()
        assert isinstance(sound, Aplay)

    def test_weigth_setup_should_be_correct(self):
        self.help_mock()
        weight = SetupPeriph.create_weight_setup()
        assert isinstance(weight, HX711Driver)

    def test_door_setup_should_be_correct(self):
        self.help_mock()
        door = SetupPeriph.create_door_setup()
        assert isinstance(door, GpioDoor)

    def test_keypad_setup_should_be_correct(self):
        self.help_mock()
        keypad = SetupPeriph.create_keypad_setup()
        assert isinstance(keypad, KeypadMatrixUart)
        patch.stopall()

  