import configparser
import sys
sys.path.append('drivers/keypad')
sys.path.append('drivers/hx711')
sys.path.append('drivers/door')
sys.path.append('drivers/usb_camera')
sys.path.append('drivers/sound')
sys.path.append('utils')

from pins_config import PinsConfig
from keypad import Keypad
from door import Door
from hx711 import Hx711
from sound import Sound
from usb_camera import UsbCamera

REFERENCE_UNIT_WEIGHT = 142 ### need to calibrate
SAMPLES = 9 # qty of data read by weight sensor at once operation.


class PeripheralOperations:
    def __init__(self ) -> None:
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
        self.door   = None
        self.camera = None


    def _set_weight_pins(self, pd_out, sck):
        self.pin_dout_weight = pd_out
        self.pin_sck_weight  = sck


    def _set_door_pins(self, door_lock, door_sense):
        self.pin_door_lock = door_lock
        self.pin_door_sense = door_sense


    def _get_data_from_config_file(self, section:str, var : str) -> str:
        parser_data  = configparser.ConfigParser()
        parser_data.read('./conf/config.ini')
        data = parser_data.get(section, var)
        return data


    def _set_dir_saved_photo(self):
        # get from config.ini
        parsed_config = self._get_data_from_config_file('usb_camera', 'photo_dir')
        self.dir_saved_photo = parsed_config


    def _set_hw_usb_camera(self):
        parsed_config = self._get_data_from_config_file('usb_camera', 'hw_addr')
        self.hw_addr_usb_camera = parsed_config


    def _get_dir_sound_files(self):
        self.sound_files_dir = self._get_data_from_config_file('dir', 'files_sound')

    
    def play_sound(self, file_name:str):
        self.sound.play(self.sound_files_dir, file_name)
        

    def set_all_pins_periphs(self):
        pins = PinsConfig()
        self._set_door_pins(pins.GPIO_DOOR_LOCK, pins.GPIO_DOOR_SENSE)
        self._set_weight_pins(pins.PD_OUT_WEIGHT, pins.SCK_WEIGHT)

    
    def init_weight(self):
        self.weight.set_reading_format("MSB", "MSB")
        self.weight.set_reference_unit(REFERENCE_UNIT_WEIGHT)
        self.weight.reset()
        self.weight.tare()

        
    def init_all(self):
        self.set_all_pins_periphs()
        self._set_hw_usb_camera()
        self.keypad = Keypad()
        self.weight = Hx711(self.pin_dout_weight, 
                            self.pin_sck_weight)
        self.door   = Door(self.pin_door_lock,
                           self.pin_door_sense)
        self.camera = UsbCamera(self.hw_addr_usb_camera)
        self.sound = Sound()
        self.init_weight()
        self._get_dir_sound_files()
        self._set_dir_saved_photo()
        self.camera.set_dir_saved_photo(self.dir_saved_photo)


    def read_input_keypad(self):
        read_char = self.keypad.reading_input_char()
        return read_char
    

    def lock_door(self):
        self.door.lock_door()


    def unlock_door(self):
        self.door.unlock_door()


    def sense_door(self):
        door_state = self.door.sense_door_state()
        return door_state


    def get_weight(self):
        weight_val = self.weight.get_weight(SAMPLES)
        # round it with 1 precision value.
        rounded_weight_val = round(weight_val, 1)
        return rounded_weight_val
    

    def set_power_down_weight(self):
        self.weight.power_down()


    def set_power_up_weight(self):
        self.weight.power_up()


    def capture_photo(self):
        self.camera.capture_photo()
    

    def delete_photo(self):
        # delete all photos
        self.camera.delete_all_photos_in_folder()

    
    def get_photo_name(self) -> list:
        file_photo_name = self.camera.get_photo_name()
        return file_photo_name
