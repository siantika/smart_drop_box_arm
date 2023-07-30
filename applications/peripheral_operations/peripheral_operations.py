"""
    File           : peripheral operations
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : July, 2023
    Description    : 

        Operations of peripherals (camera, weight sensor, GPIOs, sound, and keypad).
        For weight sensor, it is not in gram unit. I found it in other people repo(check
        hx711.py in driver folder)

"""

import configparser
import os
from pathlib import Path
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
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

# Constants 
# Hx711 driver
REFERENCE_UNIT_WEIGHT = 142  # Calibration unit for weight sensor

# Utility functions
def read_config_file(config_file_path: Path, section: str, param: str) -> str:
    '''
    Reads configuration file in 'config.ini'.
    Args:
        section (str): The section in the config file.
        param (str): The parameter in the config file
    Returns:
        value of intended param.
    Raises:
        configparser.Error: If there is an error reading the 
                                configuration file 
    '''
    parser_secret = configparser.ConfigParser()
    try:
        parser_secret.read(config_file_path)
        parsed_config_data = parser_secret.get(section, param)
    except Exception as error:
        raise configparser.Error(f'Error reading configuration file: {error}')
    return parsed_config_data


class PeripheralsSetupCreation:
    """ Factory creator for peripherals setup"""
    @staticmethod
    def create_camera_setup():
        """ Camera setup 
            It uses 640 x 480 resolution.
            camera's hardware address and directory of
            saved photo are configured in config file
        """
        camera_setting = UsbCameraSetting()
        camera_setting.resolution = CameraResolution._640x480
        camera_hw_addr = read_config_file(config_dir,
                                          'camera', 'hw_address')
        usb_camera = UsbCamera(camera_hw_addr, camera_setting)
        usb_camera.dir = read_config_file(config_dir,
                                          'camera', 'dir_to_save_photo')
        return usb_camera

    @staticmethod
    def create_sound_setup():
        """ Sound setup using Aplay media player"""
        return Aplay()

    @staticmethod
    def create_weight_setup():
        """
            Weight sensor setup
            It uses HX711 driver and 142 for ref unit
            (check weight driver and example).
            Gpio pins are configured in ConfigPins
        """
        weight = HX711Driver(PinsConfig.PD_OUT_WEIGHT,
                             PinsConfig.SCK_WEIGHT)
        weight.set_reference_unit(REFERENCE_UNIT_WEIGHT)
        weight.calibrate()
        return weight

    @staticmethod
    def create_door_setup():
        """ Gpio door setup with active low GPIO
            Gpio pins are configured in PinsConfig
        """
        return GpioDoor(PinsConfig.GPIO_DOOR_LOCK,
                        PinsConfig.GPIO_DOOR_SENSE,
                        GpioType.ACTIVE_LOW)

    @staticmethod
    def create_keypad_setup():
        """ Keypad setup using uart protocol and 9600 baudrate
            Serial port is configured in config file
        """
        keypad_port = read_config_file(config_dir, 'keypad',
                                       'port')
        return KeypadMatrixUart(keypad_port, 9600)


class PeripheralOperations:
    """ Grouping the peripherals in one class 
        Please initiates with:
          object_ex = PeripheralOperations.get_instance()
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """ Create only 1 instance when it invoke
            everywhere (Singletone)
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """ Initiate peripherals """
        self._sound = PeripheralsSetupCreation.create_sound_setup()
        self._camera = PeripheralsSetupCreation.create_camera_setup()
        self._weight = PeripheralsSetupCreation.create_weight_setup()
        self._door = PeripheralsSetupCreation.create_door_setup()
        self._keypad = PeripheralsSetupCreation.create_keypad_setup()

    @property
    def sound(self):
        """ Performs sound operations """
        return self._sound

    @property
    def camera(self):
        """ Performs camera operations """
        return self._camera

    @property
    def weight(self):
        """ Performs weight operations """
        return self._weight

    @property
    def door(self):
        """ Performs door operations """
        return self._door

    @property
    def keypad(self):
        """ Performs keypad operations """
        return self._keypad
