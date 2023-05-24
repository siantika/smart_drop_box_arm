"""
    File           : peripheral_operations.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

        Operations of peripherals (camera, weight sensor, GPIOs, sound, and keypad).
        For weight sensor, it is not in gram unit. I found it in other people repo(check
        hx711.py in driver folder)

    License: see 'licenses.txt' file in the root of project
"""

import configparser
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

sys.path.append(os.path.join(parent_dir, 'drivers/keypad'))
sys.path.append(os.path.join(parent_dir, 'drivers/hx711'))
sys.path.append(os.path.join(parent_dir, 'drivers/door'))
sys.path.append(os.path.join(parent_dir, 'drivers/usb_camera'))
sys.path.append(os.path.join(parent_dir, 'drivers/sound'))
sys.path.append(os.path.join(parent_dir, 'utils'))

#Should put here
from usb_camera import UsbCamera
from sound import Sound
from hx711 import Hx711
from door import Door
from keypad import Keypad
from pins_config import PinsConfig

REFERENCE_UNIT_WEIGHT = 142  # Calibration unit for weight sensor
SAMPLES = 9  #  frequency of sampling weight sensor data

full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')


class PeripheralOperations:
    def __init__(self) -> None:
        self.pin_dout_weight = ''
        self.pin_sck_weight = ''
        self.pin_door_lock = ''
        self.pin_door_sense = ''
        self.dir_saved_photo = ''
        self.hw_addr_usb_camera = ''
        self.sound = ''
        self.sound_files_dir = ''

        self.keypad = None
        self.weight = None
        self.door = None
        self.camera = None

    def _set_weight_pins(self, pd_out, sck)-> None:
        self.pin_dout_weight = pd_out
        self.pin_sck_weight = sck

    def _set_door_pins(self, door_lock, door_sense)-> None:
        self.pin_door_lock = door_lock
        self.pin_door_sense = door_sense

    def _get_data_from_config_file(self, section: str, var: str) -> str:
        parser_data = configparser.ConfigParser()
        parser_data.read(full_path_config_file)
        data = parser_data.get(section, var)
        return data

    def _set_dir_saved_photo(self)-> None:
        # get from config.ini
        relative_photos_folder = self._get_data_from_config_file(
            'usb_camera', 'photo_dir')
        full_path_photos_dir = os.path.join(parent_dir, relative_photos_folder)
        self.dir_saved_photo = full_path_photos_dir

    def _set_hw_usb_camera(self)-> None:
        parsed_config = self._get_data_from_config_file(
            'usb_camera', 'hw_addr')
        self.hw_addr_usb_camera = parsed_config

    def _get_dir_sound_files(self)-> None:
        relative_sound_folder = self._get_data_from_config_file(
            'dir', 'files_sound')
        self.sound_files_dir = os.path.join(parent_dir, relative_sound_folder)

    def play_sound(self, file_name: str)-> None:
        self.sound.play(self.sound_files_dir, file_name)

    def set_all_pins_periphs(self)-> None:
        pins = PinsConfig()
        self._set_door_pins(pins.GPIO_DOOR_LOCK, pins.GPIO_DOOR_SENSE)
        self._set_weight_pins(pins.PD_OUT_WEIGHT, pins.SCK_WEIGHT)

    def init_weight(self)-> None:
        self.weight.set_reading_format("MSB", "MSB")
        self.weight.set_reference_unit(REFERENCE_UNIT_WEIGHT)
        self.weight.reset()
        self.weight.tare()

    def init_all(self)-> None:
        self.set_all_pins_periphs()
        self._set_hw_usb_camera()
        self.keypad = Keypad()
        self.weight = Hx711(self.pin_dout_weight,
                            self.pin_sck_weight)
        self.door = Door(self.pin_door_lock,
                         self.pin_door_sense)
        self.camera = UsbCamera(self.hw_addr_usb_camera)
        self.sound = Sound()
        self.init_weight()
        self._get_dir_sound_files()
        self._set_dir_saved_photo()
        self.camera.set_dir_saved_photo(self.dir_saved_photo)

    def read_input_keypad(self)->str:
        read_char = self.keypad.reading_input_char()
        return read_char

    def lock_door(self)-> None:
        self.door.lock_door()

    def unlock_door(self)-> None:
        self.door.unlock_door()

    def sense_door(self)->bool:
        door_state = self.door.sense_door_state()
        return door_state

    def get_weight(self)->float:
        weight_val = self.weight.get_weight(SAMPLES)
        # Ease us to read the weight value
        rounded_weight_val = round(weight_val, 1)
        return rounded_weight_val

    def set_power_down_weight(self)-> None:
        self.weight.power_down()

    def set_power_up_weight(self)-> None:
        self.weight.power_up()

    def capture_photo(self)-> int:
        return self.camera.capture_photo()

    def delete_photo(self)-> None:
        # Actually, we delete all photos in assets/photos folder
        self.camera.delete_all_photos_in_folder()

    def get_photo_name(self) -> list:
        file_photo_name = self.camera.get_photo_name()
        return file_photo_name
