"""
    File           : Controller app
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : July, 2023
    Description    : 

        Controls app routines.
"""
import configparser
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import time
import threading
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
from display_app import DisplayApp, DisplayMode
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


def read_queue_from_net(self) -> mp.Queue:
    with self.lock:
        return None if self.queue_data_from_net.empty() \
            else self.queue_data_from_net.get(timeout=1)

def set_queue_to_lcd_thread(self, q_to_lcd: mp.Queue):
    self.queue_data_to_lcd = q_to_lcd

def set_queue_from_net_thread(self, q_from_net: mp.Queue):
    self.queue_data_from_net = q_from_net

def set_queue_to_net_thread(self, q_to_net: mp.Queue):
    self.queue_data_to_net = q_to_net

def create_payload(self, app_name: str, method, is_data_object=False, **kwargs) -> dict:
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

def send_data_queue(self, queue_thread: mp.Queue, data: dict):
    with self.lock:
        return "full" if queue_thread.full() else \
            queue_thread.put(data, timeout=1.0)

def request_data_to_server(self, payload: dict):
    get_response = None
    # all params must be initialized
    status, response = self.network.handle_commands(
        payload, auth_turn_on=True)
    get_response = response  # should return list contains no_resi
    return status, get_response

def get_image_as_binary(self, file_name: str):
    photo_path = os.path.join(full_photo_folder, str(file_name))

    with open(photo_path, 'rb') as f:
        bin_photo = f
    return bin_photo

def make_initial_data(self, data: list) -> dict:
    '''
        Make finding no resi much faster with dict.

        Args :
            data (list[str])  :  list data contains full data from API.

        Returns : 
            initial_data (dict[str, int])  : Contains no_resi and index data from
                                                temp_storage_data (the full data)

    '''
    data_initial = {}
    is_dict = True

    # filter item if in items are not dict:
    if data is not None and all(isinstance(item, dict) for item in data):
        is_dict = True
    else:
        is_dict = False

    # If data is correct, update with new data from server
    if is_dict and data is not None:
        for index, data in enumerate(data):
            temp_data_initial = {data['no_resi']: index}
            data_initial.update(temp_data_initial)

    return data_initial

def get_data_from_config(self, section: str, param: str):
    parser_ver = configparser.ConfigParser()
    parser_ver.read(full_path_config_file)
    data = parser_ver.get(section, param)
    return data

def check_universal_password(self, universal_password):
    # universal password should not exceed 4 chars and doen't contain 'D' char !
    len_pass = len(universal_password)
    if len_pass > 4 or 'D' in universal_password:
        # send data to lcd
        self._send_data_queue(self.queue_data_to_lcd,
                                LcdData.ERROR_UNIVERSAL_PASSWORD)
        log.logger.error(
            "Universal password is filled with more than 4 chars or contans 'D' char !")
        # halt system
        while True:
            pass



class ThreadOperation:
    def __init__(self) -> None:
        self.queue_data_to_lcd = mp.Queue()
        self.queue_data_to_net = mp.Queue()
        self.queue_data_from_net = mp.Queue()
        self.keypad_buffer = ''
        # store data from network
        self.temp_storage_data = []
        # concise data from temp_storage_data ('no_resi' : no_index_of_temp_storage)
        self.initial_data = {}
        self.latest_weight = None
        self.st_msg_has_not_displayed = True
        self.item_is_stored = False
        self.keypad_session_ok = False
        self.taking_item_ok = False  # state for user taking the item inside the box
        self.latest_items_data = self.temp_storage_data
        self.lock = threading.Lock()
        self.periph = PeripheralOperations()
        self.network = NetworkThread()
        self.periph.init_all()

    '''

    HIGHER METHODS

        These methods consist for perform routines in operation thread. There are 4 routines
        .
            1. Network routine
               Getting no resi from server and log the response from server. It will handle
               unfinished response (failed response) in DELETE used-no_resi and POST Image
               in 'door session'. Excuting every 'NETWORK_TIMEOUT' const secs.

            2. keypad_routine
               handle keypad input from user, check if no resi or universal password is valid.

            3. taking item routine
               handle for taking items by user (opening door, tell instructions for deleteing items
               in app). Update read weight (should be near 0.0 because empty). Only valid when universal pass 
               is inserted and match.

            4. door session
               Opening door and reading to door sense and weight sensor. There are 2 paths conditions.
               i. no weight change from last read weight and door pos == 1 (closed) -> back to first while code. it doesnt continue 
                  the sending data to server and it doesn't delete no_resi used (count as failed transaction)
               ii. weight changed from last read and door is door pos == 1 -> continue to next routine.
               
            5. final session
               Sending data image to server and send request delete for used no_resi to server. If one of them or
               both are fail, we out it on queue data send to network_routine (try again perform)
               And send notification to telegram bot
    '''

    def network_routine(self):
        queue_from_net = self._read_queue_from_net()
        if queue_from_net is not None:
            self.temp_storage_data = queue_from_net
            self.initial_data = self._make_initial_data(self.temp_storage_data)

        # only log once
        if self.latest_items_data != self.temp_storage_data:
            self.latest_items_data = self.temp_storage_data
            items_stored = None
            if self.latest_items_data != None:
                items_stored = json.dumps(self.latest_items_data)
            else:
                items_stored = "Empty"
            log.logger.info("Items tersimpan: " + items_stored)

    def keypad_routine(self, universal_password):
        self._send_data_queue(self.queue_data_to_lcd,
                              LcdData.FISRT_INPUT_KEYPAD)
        self.st_msg_has_not_displayed = True

        start_time_keypad_session = time.time()

        flag_send_to_lcd = 0

        while True:
            current_time = time.time()
            keypad_data_input = self.periph.read_input_keypad()

            if current_time - start_time_keypad_session > KEYPAD_TIMEOUT:
                self.st_msg_has_not_displayed = True
                self._send_data_queue(self.queue_data_to_lcd, LcdData.TIMEOUT)
                time.sleep(2.0)  # make LCD data display visible for user
                break

            # Send input user from keypad to LCD thread. Neglect if user input is 'D' char
            # Because it will be delete-command.
            if keypad_data_input is not None and keypad_data_input != 'D':
                self.keypad_buffer = self.keypad_buffer + \
                    str(keypad_data_input)
                flag_send_to_lcd = 1

            # Delete single char command
            if keypad_data_input == 'D':
                self.keypad_buffer = self.keypad_buffer[:-1] 
                flag_send_to_lcd = 1

            # Send data to LCD thread
            if flag_send_to_lcd == 1:
                data_lcd = self._create_payload(
                    'lcd', method='keypad', first_line='Masukan resi:', 
                    second_line=self.keypad_buffer)
                self._send_data_queue(self.queue_data_to_lcd, data_lcd)
                #reset flag
                flag_send_to_lcd = 0


            # Perform validation when keypad entered 4 times.
            if len(self.keypad_buffer) == 4:
                # Check users no _resi and no_resi stored in database with keys in dict 
                # (no_resi = keys, index = values)
                if self.keypad_buffer in self.initial_data.keys():
                    self.keypad_session_ok = True
                    self._send_data_queue(
                        self.queue_data_to_lcd, LcdData.NO_RESI_SUCCESS)
                    break
                # User input the universal password instead of valid no_resi and it's correct
                elif self.keypad_buffer == universal_password:
                    self.taking_item_ok = True
                    break
                else:
                    self._send_data_queue(
                        self.queue_data_to_lcd, LcdData.RESI_FAILED)
                    self.keypad_session_ok = False
                    time.sleep(2.0)  # make LCD data display visible for user
                    break

            self.st_msg_has_not_displayed = True

    def taking_item_routine(self):
        self.periph.unlock_door()
        self._send_data_queue(self.queue_data_to_lcd, LcdData.TAKING_ITEM)
        self.periph.play_sound(SoundData.TAKING_ITEM)
        start_time_door_session = time.time()
        door_pos = self.periph.sense_door()
        is_warned = False
        #create a sound warning thread
        sound_warning_thread = mp.Process(target= self.sound_warning_thd,)
        while door_pos != 1:
            current_time = time.time()
            door_pos = self.periph.sense_door()

            if current_time - start_time_door_session > DOOR_TIMEOUT and is_warned == False:
                is_warned = True
                self._send_data_queue(
                    self.queue_data_to_lcd, LcdData.DOOR_ERROR)
                sound_warning_thread.start()

        self.periph.lock_door()
        # kill the sound warning thread 
        if sound_warning_thread.is_alive() == True:
            sound_warning_thread.kill()

        is_warned = False
        
        # get the latest weight of empty box.
        self.periph.set_power_up_weight()
        time.sleep(0.1)
        self.latest_weight = self.periph.get_weight()
        self.periph.set_power_down_weight()

        self._send_data_queue(self.queue_data_to_lcd,
                              LcdData.AFTER_TAKING_ITEM)
        
        #delay for sound operation
        time.sleep(1.5)
        self.periph.play_sound(SoundData.INSTRUCTION_DEL_ITEM)

        log.logger.info("Berat barang : " + str(self.latest_weight))
        log.logger.info("Barang telah diambil pemilik")

    def door_session(self):
        self.periph.play_sound(SoundData.POSE_COURIRER)
        time.sleep(1)
        self.periph.play_sound(SoundData.TAKING_PICTURE)

        #taking a photo
        self.periph.capture_photo()
        # check photo, if photo doesn't exist, log it as an error
        is_photo = len(self.periph.get_photo_name())
        if is_photo == 0:
             log.logger.error("Camera is error !")  

        time.sleep(0.8)

        self.periph.unlock_door()
        self.periph.play_sound(SoundData.PUT_ITEM)

        # wake up sensor weight
        self.periph.set_power_up_weight()
        time.sleep(0.1)

        # warning signs flag
        is_warned = False

        # create a sound warning thread
        process_sound_warning = mp.Process(target=self.sound_warning_thd, )

        start_time_door_session = time.time()

        while True:
            current_time = time.time()

            read_weight = self.periph.get_weight()
            door_pos = self.periph.sense_door()

            # Item received
            if read_weight > self.latest_weight + WEIGHT_OFFSET and door_pos == 1:
                self.periph.lock_door()
                # we should kill (brute force) the thread not terminate it !
                if process_sound_warning.is_alive() == True:
                    process_sound_warning.kill()
                
                self.item_is_stored = True

                # update latest weight when item is stored
                self.latest_weight = read_weight
                log.logger.info("Barang dengan no resi " + self.keypad_buffer + " telah disimpan \
                                    di dalam box.")
                break

            # No item received
            elif read_weight < self.latest_weight + WEIGHT_OFFSET and door_pos == 1:
                self.periph.lock_door()
                # we should kill (brute force) the thread not terminate it !
                if process_sound_warning.is_alive() == True:
                    process_sound_warning.kill()
                
                self.item_is_stored = False    
                self.periph.lock_door()  # suddenly lock the door.
                self._send_data_queue(
                    self.queue_data_to_lcd, LcdData.NO_ITEM_RECEIVED)
                time.sleep(2.0)  # make LCD data display visible  for user and give sound to play again
                self.periph.play_sound(SoundData.BARANG_BELUM_DITERIMA)
                log.logger.warning(
                    "Barang dengan no resi " + self.keypad_buffer + " tidak disimpan di dalam box!!!")
                break

            # warning signs
            # execute once
            if current_time - start_time_door_session > DOOR_TIMEOUT and is_warned == False:
                is_warned = True
                process_sound_warning.start()
                self.item_is_stored = False
                self._send_data_queue(
                    self.queue_data_to_lcd, LcdData.DOOR_ERROR)
                log.logger.critical(
                    "Pintu dibiarkan terbuka untuk no resi " + self.keypad_buffer + ".")
        

        # put the weight sensor sleep
        self.periph.set_power_down_weight()
        log.logger.info("Berat barang : " + str(self.latest_weight))
        self.st_msg_has_not_displayed = True


    def final_session(self):
        bin_photo = None
        photo_file_name = None
        payload = {}

        self._send_data_queue(self.queue_data_to_lcd, LcdData.THANKYOU)
        time.sleep(2)
        self.periph.play_sound(SoundData.ACCEPTED_ITEM)

        # get all photos file names
        list_of_photos_file_name = self.periph.get_photo_name()
        # check if photo is exist
        if len(list_of_photos_file_name) != 0:
            photo_file_name = list_of_photos_file_name[0]
            # data photo has to be in binary type
            last_foto_path = os.path.join(full_photo_folder, photo_file_name)
            with open(last_foto_path, 'rb') as f:
                bin_photo = f.read()
        else:
            bin_photo = ""
            photo_file_name = "tidak ada photo"

        payload_delete_finished_resi = {
            'method': 'DELETE', 'payload': {'no_resi': self.keypad_buffer}}

        self._send_data_queue(self.queue_data_to_net,
                              payload_delete_finished_resi)

        # Get data stored in this session.
        index = self.initial_data[self.keypad_buffer]
        payload = self.temp_storage_data[index]

        # create photo payload with param 'photo' and value are file name and photo in bin format.
        # it will send data in FILES (uploaded file) HTTPS.
        payload_photo = {'photo': (photo_file_name, bin_photo)}
        # update payload data with data photo in bin format.
        payload.update(payload_photo)
        # create full payload for success_item API
        payload_success_item = self._create_payload(
            'network', method='success_items', is_data_object=True, data_object=payload)

        # send to net thread (avoid blocking process for requests to server)
        self._send_data_queue(self.queue_data_to_net, payload_success_item)

        # send notification to telegram bot
        status_telegram = Telegram.send_notification(payload, bin_photo)

        print("status code telegram: " + str(status_telegram))

        # make lcd dispaly first message (Tekan keypad ...)
        self.st_msg_has_not_displayed = True

    def clean_all_global_var_and_photo(self):
        self.keypad_buffer = ''
        self.keypad_session_ok = False
        self.item_is_stored = None
        self.taking_item_ok = None

        # only delete when photo is exist in 'photos' folder
        len_photo_file_name = len(self.periph.get_photo_name())
        if len_photo_file_name != 0:
            self.periph.delete_photo()
            log.logger.info("Foto berhasil dihapus!")

    def run(self):
        '''
            Driver code
        '''
        keypad_is_pressed = None
        # get and check universal password
        UNIVERSAL_PASSWORD = self.get_data_from_config(
            'pass', 'universal_password')
        self.check_universal_password(UNIVERSAL_PASSWORD)

        # get data from network thread
        if self._read_queue_from_net() is not None:
            self.temp_storage_data = self._read_queue_from_net()
            self.initial_data = self._make_initial_data(self.temp_storage_data)

        # get the first weight read
        self.periph.set_power_up_weight()
        time.sleep(0.1)
        self.latest_weight = self.periph.get_weight()
        self.periph.set_power_down_weight()  # make weight sensor sleep!
        log.logger.info("Berat barang : " + str(self.latest_weight))

        while True:
            keypad_is_pressed = self.periph.read_input_keypad()
            # listening to network thread
            self.network_routine()

            if self.st_msg_has_not_displayed:
                self.st_msg_has_not_displayed = False
                self._send_data_queue(self.queue_data_to_lcd, LcdData.ST_MSG)

            if keypad_is_pressed is not None:
                self.keypad_routine(UNIVERSAL_PASSWORD)

            # These processes is determined by keypad_routine !
            if self.taking_item_ok:
                self.taking_item_routine()

            if self.keypad_session_ok:
                self.door_session()

            # This process is determined by door_session!
            if self.item_is_stored:
                self.final_session()

            self.clean_all_global_var_and_photo()

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

@dataclass
class NoResi:
    """ Key data to find full information of items data """
    value_4_digits:str 

@dataclass 
class DoorPassword:
    """ Password for opening door """
    password: str 

@dataclass
class FilePhoto:
    """ Captured photo """ 
    bin_data : bytes 

@dataclass
class ItemsWeght:
    """ Item weight (no unit)
        It means reading item according default
        unit (it very sensitive, even a piece of paper
        will be weighted/read)
    
    """
    no_unit_value: float


""" Use case """
class GetDataItems:
    """ Fetching and storing data items from data sources/server"""
    def get(self, queue_data:mp.Queue, data_item:DataItem)-> None | DataItem:
        """ Reads existing data from data source using
            queue. Non blocking operation applied. Since
            this app needs to execute another processes
            (main controller) in almost simultaneously.
            Args:
                queue_data (mp.Queue) : queue data for receiving
                data from other thread.
                data_item (DataItem) : data item entity from 
                data sources/server
            Returns:
                data items (DataItem) or None if no data in queue
        """
        raw_data_items = None if queue_data.get(False, timeout=1) else None
        if raw_data_items != None:
            data_item.no_resi = raw_data_items['no_resi']
            data_item.item = raw_data_items['item']
            data_item.date_ordered = raw_data_items['date_ordered']
            return data_item
        return None


class GetNoResi:
    """ Get no resi from user """
    GET_RESI_TIMEOUT = 15 # secs

    def _determinator(self, no_resi_buffer:list,
                       single_char:str,  queue_data:mp.Queue)-> None:
        """ Determine behaviours of no resi gettig from
            Keypad.
            Args:
                queue_data (mp.Queue) : queue data to display
                                        app
            """ 
        if single_char is not None and single_char is not 'D':
            no_resi_buffer.append(single_char)
            # send to display app 
            queue_data.put(
                {
                'cmd' : DisplayMode.NORMAL,
                'payload' : ['Masukan resi:', "".join(no_resi_buffer)]
                }
            )
        # Delete the latest char in no resi buffer
        if single_char is 'D':
            no_resi_buffer.pop()
            # send coverted list to string to display app queue
            queue_data.put(
                {
                'cmd' : DisplayMode.NORMAL,
                'payload' : ['Masukan resi:', "".join(no_resi_buffer)]
                }
            )
        
    def get(self, no_resi:NoResi, interface:PeripheralOperations,
            display_app_queue:mp.Queue) -> NoResi:
        """ Get no resi from user """
        no_resi_buffer:str = ""
        start_time = time.time()
        while time.time() - start_time < self.GET_RESI_TIMEOUT or len(no_resi_buffer) <= 4:
            a_char_of_no_resi = interface.keypad.reading_input_char()
            self._determinator(a_char_of_no_resi, display_app_queue)
        no_resi.value_4_digits = no_resi_buffer
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
    def process(periph:PeripheralOperations, last_weight:ItemsWeght,
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



