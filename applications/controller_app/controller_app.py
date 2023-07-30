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
sys.path.append(os.path.join(parent_dir, 'utils'))

# Should put here due to DIY libs (we built it and it locates in our project dirs.)
from telegram_app import TelegramApp
from data_transactions_app import HttpSendDataApp
from peripheral_operations import PeripheralOperations
from display_app import DisplayMode
from media_data import LcdData, SoundData
import log

# telegram app object
Telegram = TelegramApp()

full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')
full_photo_folder = os.path.join(parent_dir, 'assets/photos/')

# TIMEOUT in secs
KEYPAD_TIMEOUT = 15
DOOR_TIMEOUT = 15
NETWORK_TIMEOUT = 5
# Compesate error read by weight sensor due to electrical issue
WEIGHT_OFFSET = 1.0


# New code
def create_payload_for_queue_apps(app_name: str, method, 
                                  is_data_object=False, **kwargs) -> dict:
    lines = None
    data_object = {}
    lc_app_name = str.lower(app_name)

    if lc_app_name == 'lcd':
        if is_data_object:
            data_object = {'method': method}
            payload = {'payload': kwargs['data_object']}
            data_object.update(payload)
        else:
            lines = [kwargs[key] for key in ['first_line', 'second_line']
                        if key in kwargs]

            # Raise value error when lines don't have intended params
            len_of_lines = len(lines)
            len_of_params = len(kwargs.values())
            if len_of_lines != 2 or len_of_params != 2:
                raise ValueError(
                    "Lcd parameters should be only 'first_line' and 'second_line'!")

            payload = {'payload': lines}
            data_object = {'cmd': method}
            data_object.update(payload)

    if lc_app_name == 'network':
        if is_data_object:
            data_object = {'method': method}
            payload = {'payload': kwargs['data_object']}
            data_object.update(payload)
        else:
            data_object = {'method': method}
            data_object.update(kwargs)
    return data_object


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

        if len(self.value_4_digits) > 4 or len(self.value_4_digits) < 4:
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
        no_resi_buffer:list = []
        start_time = time.time()
        while time.time() - start_time < self.GET_RESI_TIMEOUT or len(no_resi_buffer) <= 4:
            user_input_char = interface.keypad.reading_input_char()
            self._determinator(no_resi_buffer, user_input_char, display_app_queue)
        # covert list to string
        no_resi = NoResi("".join(no_resi_buffer))
        return no_resi

            
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
        target_data_item:DataItem 

        if no_resi.value_4_digits in available_data_items.keys():
            target_data_item.no_resi = available_data_items[no_resi.value_4_digits][0]
            target_data_item.item = available_data_items[no_resi.value_4_digits][1]
            target_data_item.date_ordered = available_data_items[no_resi.value_4_digits][2]
            return target_data_item
        
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


class TakingItems:
    """ Performs taking-items routine inside the box routine 
        Condition to excute: Should pass door password validation
        Routines: openning the door, playing 'instruction sound',
        read weight (should be near 0 because no items inside the box)

    """
    def process(self, periph:PeripheralOperations, ):
        periph.door.unlock()
        periph.sound.play(SoundData.TAKING_ITEM)
        while True:
            time.time()
            if periph.door.sense_door_state == False:
                break
            if periph.door.sense_door_state == True and time.time() > DOOR_TIMEOUT:
                if periph.sound.play(SoundData.WARNING_DOOR_OPEN) == None:
                    pass 



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
        with open(photo_file, 'rb') as f:
            bin_photo = f
        return bin_photo

    def process(self, periph:PeripheralOperations, photo:FilePhoto):
        """ Taking a picture 
            Args:
                periph : Peripheral operations acessing sound and camera
                photo (byte): photo in binary format
            Returns:
                photo in binary format (byte)
        """
        periph.sound.play(SoundData.POSE_COURIRER)
        periph.sound.play(SoundData.TAKING_PICTURE)
        periph.camera.capture_photo()
        photo.bin_data = self._get_photo_file_as_binary()
        return photo


class ReceivingItems:
    """
        Performs receiving-items routine.
        Condition to excute: Should pass no resi validation
        Routines: openning door, reading door position and weighting,
        Checking door postion and change in item weight, and alert if door 
        is open for certain time.
        NOTE:
        Conditions of door position and weigh:
            1. If door is closed and no change in item weight, it will play 
               "No item stored" sound.
            2. If door position is open exceeding door timeout, It will play
               alert sound until door is closed.
            3. If door position close and there is change in item weight, it will
               play " Item successfully stored " and return success operation 
    """    
    @staticmethod
    def process(periph:PeripheralOperations, last_weight:ItemsWeight,
                queue_to_display:mp.Queue):
        periph.door.unlock()
        start_time = time.time()
        while True:
            # Condition 1
            if periph.door.sense_door_state() == True and \
            periph.weight.get_weight() == last_weight:
                periph.sound.play()
                queue_to_display.put(LcdData.NO_ITEM_RECEIVED)
                break
            # Condition 2
            if time.time() - start_time > DOOR_TIMEOUT:
                periph.sound.play()
            # Condition 3
            if periph.door.sense_door_state() == True and \
            periph.weight.get_weight() > last_weight:
                periph.sound.play()
                queue_to_display.put(LcdData.ITEM_RECEIVED)
                break


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
        payload.update['endpoint'] = 'delete.php'
        payload.update['data'] = data_to_dict
        payload.update['http_header'] = http_header
        return payload

    def _send_post_multipart_requests(self, target_data_item:DataItem,
                             file_photo:FilePhoto) -> dict:
        payload = {}
        data_to_dict = {
            'no_resi' : target_data_item.no_resi,
            'item' : target_data_item.item,
            'date_ordered' : target_data_item.date_ordered
        } 
        http_header = {'content-type' : 'application/json'}
        payload.update['endpoint'] = 'success_item.php'
        payload.update['data'] = data_to_dict
        payload.update['http_header'] = http_header
        payload.update['file'] = file_photo.bin_data
        return payload

    def process(self, queue_to_data_access:mp.Queue,
                target_data_item: DataItem, 
                file_photo: FilePhoto) -> None:
        delete_request = self._send_delete_requests(target_data_item)
        post_multipart_request = self._send_post_multipart_requests(target_data_item, 
                                                                    file_photo)
        # send to data access queue
        try:
            queue_to_data_access.put_nowait(delete_request)
            queue_to_data_access.put_nowait(post_multipart_request)
        except queue_to_data_access.full():
            pass 


class Notify:
    """ Notify the user throught medias"""
    @staticmethod
    def telegram_notification(self, target_data_item: DataItem,
                              file_photo:FilePhoto)->int:
        """ Send a notification to telegram bot 
            Args:
                target_data_item(DataItem): selected data item
                file_photo(FilePhoto): File photo for sending photo
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
                                          file_photo.bin_data) 



