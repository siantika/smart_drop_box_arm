"""
    File           : Controller app
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : July, 2023
    Description    : 

        Controls app routines.
"""
import configparser
from dataclasses import dataclass
import os
from pathlib import Path
import queue
import sys
import time
import multiprocessing as mp
from typing import Any

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

sys.path.append(os.path.join(parent_dir, 'applications/peripheral_operations'))
sys.path.append(os.path.join(parent_dir, 'applications/data_transactions_app'))
sys.path.append(os.path.join(parent_dir, 'applications/display_app'))
sys.path.append(os.path.join(parent_dir, 'applications/telegram_app'))
sys.path.append(os.path.join(parent_dir, 'drivers/data_access'))
sys.path.append(os.path.join(parent_dir, 'utils'))

# Should put here due to DIY libs (we built it and it locates in our project dirs.)
from telegram_app import TelegramApp
from data_transactions_app import HttpSendDataApp
from peripheral_operations import PeripheralOperations
from display_app import DisplayMode
from media_data import LcdData, SoundData
from data_access import HttpDataAccess
import log

# telegram app object
Telegram = TelegramApp()

full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')
full_photo_folder = os.path.join(parent_dir, 'assets/photos/')

# TIMEOUT in secs
KEYPAD_TIMEOUT = 6
DOOR_TIMEOUT = 10
NETWORK_TIMEOUT = 5
# Compensate error read by weight sensor due to electrical issue
WEIGHT_OFFSET = 1.0


""" Utility Functions """
def read_config_file(section:str, option:str)-> str:
    """ Read intended data from config file """
    file = configparser.ConfigParser()
    file.read(full_path_config_file)
    raw_data =  file.get(section, option)
    return raw_data

""" Entitites for bussines logics """
@dataclass
class DataItem:
    """ Data items available in data sources """
    no_resi:str
    item:str 
    date_ordered:str

    def __post_init__(self):
        """ Added data type checks """
        if not isinstance(self.no_resi, str):
            raise TypeError("Attribute 'no_resi' should be a string.")
        if not isinstance(self.item, str):
            raise TypeError("Attribute 'item' should be a string.")
        if not isinstance(self.date_ordered, str):
            raise TypeError("Attribute 'date_ordered' should be a string.")

@dataclass
class NoResi:
    """ Key data to find full information of items data """
    value_4_digits:str 

    def __post_init__(self):
        if not isinstance(self.value_4_digits, str):
            raise TypeError("Attribute 'value_4_digits' should be as a string.")

        if len(self.value_4_digits) > 4:
            raise ValueError("'Value_4_digits' should be 4 chars only ")

@dataclass 
class DoorPassword:
    """ Password for opening door """
    password: str

    def __post_init__(self):
        if not isinstance(self.password, str):
            raise TypeError("Attribute 'password' should be as a string.")

@dataclass
class FilePhoto:
    """ Captured photo """ 
    bin_data : bytes 

    def __post_init__(self):
        if not isinstance(self.bin_data, bytes):
            raise TypeError("Attribute 'bin_data' should be as a bytes.")

@dataclass
class ItemsWeight:
    """ Item weight (no unit)
        It means reading item according to default
        unit (it is very sensitive, even a piece of paper
        will be weighted/read)
    
    """
    unit_weight: float

    def __post_init__(self):
        if not isinstance(self.unit_weight, float):
            raise TypeError("Attribute 'unit_weight' should be as a float.")


""" Use cases """
class DataItemRoutines:
    """ Fetching and storing data items from data sources/server """

    def _get_data_from_queue(self, queue: mp.Queue)-> DataItem | None:
        """ Gets a data from queue
            Args:
                queue (mp.Queue) : queue data 
            Returns:
                Data items (DataItem) or None if no data in queue.
        """
        return queue.get_nowait() if not queue.empty() else None

    def get(self, queue_data: mp.Queue) -> DataItem | None:
        """Reads existing data from data source using queue.
        Args:
            queue_data (mp.Queue): Queue data for receiving data from other threads.
        Returns:
            Data items (DataItem) or None if no data in queue.
        """
        raw_data_items = self._get_data_from_queue(queue_data)
        if raw_data_items:
            data_item = DataItem(
                no_resi=raw_data_items['no_resi'],
                item=raw_data_items['item'],
                date_ordered=raw_data_items['date_ordered']
            )
            return data_item
        return None


class UserInputNoResi:
    """ Get no resi from user """
    GET_RESI_TIMEOUT = 10 # secs

    def _determinator(self, no_resi_buffer:list,
                       single_char:str,  queue_data:mp.Queue)-> None:
        """ Determine behaviours of no resi gettig from
            Keypad.
            Args:
                queue_data (mp.Queue) : queue data to display
                                        app
            """ 
        if single_char is not None and single_char != 'D':
            no_resi_buffer.append(single_char)
            # send to display app 
            queue_data.put(
                {
                'cmd' : DisplayMode.NORMAL,
                'payload' : ['Masukan resi:', "".join(no_resi_buffer)]
                }
            )
        # Delete the latest char in no resi buffer
        if single_char == 'D':
            no_resi_buffer.pop()
            # send coverted list to string to display app queue
            queue_data.put(
                {
                'cmd' : DisplayMode.NORMAL,
                'payload' : ['Masukan resi:', "".join(no_resi_buffer)]
                }
            )
        
    def get(self, interface:PeripheralOperations,
            display_app_queue:mp.Queue) -> NoResi:
        """ Get chars inputted by user 
            Args:
                interface
            Returns:
                No resi inputted by user (NoResi)
        """
        str_no_resi:str
        no_resi_buffer:list = []
        start_time = time.time()
        while (time.time() - start_time < self.GET_RESI_TIMEOUT) and len(no_resi_buffer) < 4:
            user_input_char = interface.keypad.reading_input_char()
            self._determinator(no_resi_buffer, user_input_char, display_app_queue)
        # Check user input for existing no resi
        str_no_resi = "".join(no_resi_buffer) if user_input_char else ''
        return NoResi(str_no_resi)

            
class Validation:
    """ Check and validate inputted user 
        It validates:
            1. No resi inputted by user
            2. Door password  inputted by user
    """
    @staticmethod
    def validate_no_resi(no_resi:NoResi, 
                         available_data_items:dict) -> DataItem | None:
        """ Validates no resi inputted by user
            Rules:
                1. It consists from 4 chars
                2. Should exist in data items available (variable)
            Args:
                no_resi (str): no resi inputted by user.
            Returns:
                target data item if no resi exist else None

        """
        if no_resi.value_4_digits in available_data_items.keys():
            target_data = available_data_items[no_resi.value_4_digits]
            return DataItem(
                target_data['no_resi'],
                target_data['item'],
                target_data['date_ordered']
            )
        return None
         

    @staticmethod
    def validate_door_password(password:DoorPassword, door_pass:str):
        """ Validates door password inputted by user
            Rules:
                1. It consists from 4 chars
                2. Should exist in config file (section: door_password)
            Args:
                password (str): password in chars inputted by user.
                door_pass (str) : Valid password
            Returns:
                Validation status (bool): True is valid and False is
                invalid

        """
        return True if password is door_pass else False


class TakingItem:
    """ Performs taking-items routine inside the box routine 
        Condition to excute: Should pass door password validation
        Routines: openning the door, playing 'instruction sound',
        read weight (should be near 0 because no items inside the box)

    """
    def process(periph:PeripheralOperations)-> ItemsWeight:
        sound_thread:mp.Process = None
        item_weight = 0.0
        is_sound_warning_played:bool = False
        periph.door.unlock()
        periph.sound.play(SoundData.TAKING_ITEM, True)
        time_start = time.time()
        while True:
            if periph.door.sense_door_state() == False: 
                periph.door.lock()
                if sound_thread is not None:
                    periph.sound.stop(sound_thread)
                item_weight = periph.weight.get_weight()
                log.logger.info(f"Barang telah di ambil")
                break
            if periph.door.sense_door_state() == True and \
                (time.time() - time_start > DOOR_TIMEOUT) and\
                    is_sound_warning_played == False:
                
                is_sound_warning_played = True
                sound_thread = periph.sound.play\
                    (SoundData.WARNING_DOOR_OPEN, False, True)
        return ItemsWeight(item_weight)          


class TakingPhoto:
    """ Play instruction sound and take the courier photo once 
        It convert the file photo to binary data format.
    """
    def _get_photo_file_as_binary(self, photo_file: Path):
        """ Converts jpg filephoto to binary format 
            File name with the full path.
            Args:
                photo_file (Path) : Full path of photo file
            Returns:
                photo in binary format (byte)
        """
        bin_photo = None
        with open(photo_file, 'rb') as f:
            bin_photo = f.read()
        return bin_photo

    def process(self, periph:PeripheralOperations)-> FilePhoto:
        """ Taking a picture 
            Args:
                periph : Peripheral operations acessing sound and camera
                photo (byte): photo in binary format
            Returns:
                photo in binary format (byte)
        """
        periph.sound.play(SoundData.POSE_COURIRER)
        periph.sound.play(SoundData.TAKING_PICTURE)
        file_path = periph.camera.capture_photo()[1]
        photo_in_bin_data = self._get_photo_file_as_binary(file_path)
        return FilePhoto(photo_in_bin_data)


class ReceivingItem:
    """
        Performs receiving-items routine.
        Condition to excute: Should pass no resi validation
        Routines: openning door, reading door position and weighting,
        Checking door postion and changed in item weight, and alert if door 
        is open for certain time (exceeded TIME_DOOR_TIMEOUT).
        NOTE:
        Conditions of door position and weigh:
            1. If door is closed and no change in item weight, it will play 
               "No item stored" sound and display the message respectively to condition.
            2. If door position is opened and exceeding the timeout, It will play
               alert sound until door is closed.
            3. If door position is closed and there is a change in item weight, it will
               play " Item successfully stored " and return success operation.

        Returns: New item weight (ItemWeight).
    """    
    def process(self, periph:PeripheralOperations, last_weight:ItemsWeight,
                queue_to_display:mp.Queue)-> ItemsWeight:
        is_warn_sound_played = False
        new_weight = 0.0
        periph.door.unlock()
        start_time = time.time()
        while True:
            new_weight = periph.weight.get_weight()
            # Condition 1
            if periph.door.sense_door_state() == False and \
            new_weight <= last_weight.unit_weight:
                periph.door.lock()
                periph.sound.play(SoundData.BARANG_BELUM_DITERIMA)
                queue_to_display.put(LcdData.NO_ITEM_RECEIVED)
                # Delay for putting data in queue 
                time.sleep(0.3)
                break
            # Condition 2
            if (time.time() - start_time > DOOR_TIMEOUT) and \
            is_warn_sound_played == False:
                is_warn_sound_played = True
                periph.sound.play(SoundData.WARNING_DOOR_OPEN, False, True)
            # Condition 3
            if periph.door.sense_door_state() == False and \
            new_weight > last_weight.unit_weight:
                periph.sound.play(SoundData.ACCEPTED_ITEM)
                queue_to_display.put(LcdData.ITEM_RECEIVED)
                # Delay for putting data in queue 
                time.sleep(0.3)
                break
        return ItemsWeight(new_weight)


class ProcessingData:
    """ Performs data process (to data source / server) 
        Condition to excute: Should pass receiving item with
        success operation.
        Routines: Tell data sources/server that item data with
        successfully validate no resi has arrived. So it should be deleted
        from avalable data item (in data sources/server and stored item data in global var.
        It also tell the data sources / server to update success items 
        (arrived system) including courier's photo.

    """
    def _send_delete_requests(self, target_data_item:DataItem)\
          -> dict:
        payload = {}
        data_to_dict = {
            'no_resi' : target_data_item.no_resi
        } 
        http_header = {'content-type' : 'application/json'}
        payload['endpoint'] = 'delete.php'
        payload['data'] = data_to_dict
        payload['http_header'] = http_header
        return payload

    def _send_post_multipart_requests(self, target_data_item:DataItem,
                             bin_data_photo:bytes) -> dict:
        payload = {}
        data_to_dict = {
            'no_resi' : target_data_item.no_resi,
            'item' : target_data_item.item,
            'date_ordered' : target_data_item.date_ordered
        } 
        http_header = {'content-type' : 'application/json'}
        payload['endpoint'] = 'success_item.php'
        payload['data'] = data_to_dict
        payload['http_header'] = http_header
        payload['file'] = bin_data_photo
        return payload

    def process(self, queue_to_data_access:mp.Queue,
                target_data_item: DataItem, 
                file_photo: FilePhoto) -> None:
        delete_request = self._send_delete_requests(target_data_item)
        post_multipart_request = self._send_post_multipart_requests(target_data_item, 
                                                                    file_photo)
        # Send data to data-access queue
        try:
            queue_to_data_access.put_nowait(delete_request)
            queue_to_data_access.put_nowait(post_multipart_request)
            # give time for queue to putting the data
            time.sleep(0.3)
        except queue.Full:
            pass 


class Notify:
    """ Notify the user throught medias"""
    @staticmethod
    def send_telegram_notification(target_data_item: DataItem,
                              bin_data_photo)->int:
        """ Send a notification to telegram bot 
            Args:
                target_data_item(DataItem): selected data item
                bin_data_photo(bytes): File photo for sending photo
                                        to telegram bot
            Returns:
                http status code (int)
        """
        data_to_dict:dict = {
            'no_resi' : target_data_item.no_resi,
            'item' : target_data_item.item,
        }
        telegram = TelegramApp()
        return telegram.send_notification(data_to_dict, 
                                          bin_data_photo) 
    
class Registration:
    """ Registration operations for device to the server """
    @staticmethod
    def register_device()-> bool:
        """ Register the device to the server 
            Retruns:
                registered status (bool) 
        """
        base_server = read_config_file('server', 'address')
        device_version = read_config_file('device-info', 'version')
        serial_number = read_config_file('device-info', 'serial_number')
        register_http = HttpDataAccess(base_server)
        http_header = {'content-type':'application/json'}
        data = {
            'serial_number' : serial_number,
            'device_version' : device_version
        }
        resp = register_http.post(data, 'device-register.php', http_header,
                           None, 5)
        if resp[0] == 200:
            os.environ['API_KEY'] = resp[1]['api_key']
            os.environ['OWNER'] = resp[1]['owner']
            date_registered = resp[1]['date_registered']
            log.logger.info(f"Device ini telah terhubung ke server pada {date_registered} dengan pemilik {os.environ.get('OWNER')} ")
            return True
        return False




        

        

    



