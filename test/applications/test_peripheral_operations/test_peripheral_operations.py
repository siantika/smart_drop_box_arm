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
        self._mock_serial = patch('serial.Serial', spec=serial.Serial).start()


class TestPeripheralsSetupCreation(MockResources):
    """ Test user-define settings. For camera and keypad

       """

    def test_camera_setup_should_be_correct(self):
        camera = SetupPeriph.create_camera_setup()
        assert isinstance(camera, UsbCamera)

    def test_sound_setup_should_be_correct(self):
        sound = SetupPeriph.create_sound_setup()
        assert isinstance(sound, Aplay)

    def test_weigth_setup_should_be_correct(self):
        weight = SetupPeriph.create_weight_setup()
        assert isinstance(weight, HX711Driver)

    def test_door_setup_should_be_correct(self):
        door = SetupPeriph.create_door_setup()
        assert isinstance(door, GpioDoor)

    def test_keypad_setup_should_be_correct(self):
        self.help_mock()
        keypad = SetupPeriph.create_keypad_setup()
        assert isinstance(keypad, KeypadMatrixUart)
        patch.stopall()

    
class TestPeripheralOperations(MockResources):
    """ Test peripheral operations class """
    
    def test_with_multiple_initiations(self):
        """ Shoudl return the same object 
            (Singletone)
        """
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        periph_2 = PeripheralOperations.get_instance()
        assert periph is periph_2



  