"""
    File           : operation_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

        Main thread for orechestrating other threads.

    License: see 'licenses.txt' file in the root of project
"""
import configparser
import json
import os
import sys
import time
import threading
import multiprocessing as mp

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

sys.path.append(os.path.join(parent_dir, 'applications/peripheral_operations'))
sys.path.append(os.path.join(parent_dir, 'applications/network_thread'))
sys.path.append(os.path.join(parent_dir, 'applications/telegram_app'))
sys.path.append(os.path.join(parent_dir, 'utils'))

# Should put here due to DIY libs (we built it and it locates in our project dirs.)
from telegram_app import TelegramApp
from network_thread import NetworkThread
from peripheral_operations import PeripheralOperations
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

    def _read_queue_from_net(self) -> mp.Queue:
        with self.lock:
            return None if self.queue_data_from_net.empty() \
                else self.queue_data_from_net.get(timeout=1)

    def set_queue_to_lcd_thread(self, q_to_lcd: mp.Queue):
        self.queue_data_to_lcd = q_to_lcd

    def set_queue_from_net_thread(self, q_from_net: mp.Queue):
        self.queue_data_from_net = q_from_net

    def set_queue_to_net_thread(self, q_to_net: mp.Queue):
        self.queue_data_to_net = q_to_net

    def _create_payload(self, app_name: str, method, is_data_object=False, **kwargs) -> dict:
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

    def _send_data_queue(self, queue_thread: mp.Queue, data: dict):
        with self.lock:
            return "full" if queue_thread.full() else \
                queue_thread.put(data, timeout=1.0)

    def _request_data_to_server(self, payload: dict):
        get_response = None
        # all params must be initialized
        status, response = self.network.handle_commands(
            payload, auth_turn_on=True)
        get_response = response  # should return list contains no_resi
        return status, get_response

    def _get_image_as_binary(self, file_name: str):
        photo_path = os.path.join(full_photo_folder, str(file_name))

        with open(photo_path, 'rb') as f:
            bin_photo = f
        return bin_photo

    def _make_initial_data(self, data: list) -> dict:
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
            
    # sound function to become a thread
    def sound_warning_thd(self):
        while True:
            self.periph.play_sound(SoundData.WARNING_DOOR_OPEN)

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
               is inserted and valid.

            4. door session
               Opening door and reading to door sense and weight sensor. There are 2 paths conditions.
               i. no weight change from last read weight and door pos == 1 (closed) -> back to first while code. it doesnt continue 
                  the sending data to server and it doesnt delete no_resi used (count as failed transaction)
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
