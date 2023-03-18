import configparser
import sys
import time
import queue
import threading

sys.path.append('applications/peripheral_operations')
sys.path.append('applications/network')

from peripheral_operations import PeripheralOperations
from network import Network


### LCD CONST DATA
LCD_DATA_TIMEOUT = {
    'cmd' : 'keypad',
    'payload' : ['INFO:', '-> Waktu habis!']
}
LCD_DATA_ST_MSG = {
    'cmd' : 'routine',
    'payload' : ["Tekan keypad", "untuk memulai .."]
}
LCD_DATA_RESI_VALID = {
    'cmd' : 'keypad',
    'payload' : ["INFO:", "NO RESI VALID !."]
}
LCD_DATA_RESI_FAILED = {
    'cmd' : 'keypad',
    'payload' : ["STATUS:", "RESI TIDAK ADA"]
}
LCD_DATA_DOOR_ERROR = {
    'cmd' : 'routine',
    'payload' : ["WARNING:", "TUTUP PINTU!"]
}
LCD_DATA_NO_ITEM = {
    'cmd' : 'routine',
    'payload' : ["INFO:", "Brg tidak masuk!"]
}
LCD_DATA_THANKYOU = {
    'cmd' : 'routine',
    'payload' : ["  * DITERIMA *", "  Terima kasih!"]
}
LCD_DATA_NO_ITEM_RECEIVED = {
    'cmd' : 'routine',
    'payload' : ["WARNING:", "Brg tidak ada!"]
}
LCD_DATA_ITEM_RECEIVED = {
    'cmd' : 'routine',
    'payload' : ['INFO:', '-> BRG DIAMBIL!']
}
LCD_DATA_NO_RESI_SUCCESS = {
    'cmd' : 'keypad',
    'payload' : ['STATUS:', ' RESI DITERIMA!']  
}
LCD_DATA_GET_SUCCESS = {
    'cmd' : 'routine',
    'payload' : ['STATUS REQUEST:', ' Berhasil (200)!']  
}
LCD_DATA_FISRT_INPUT_KEYPAD = {
    'cmd' : 'keypad',
    'payload' : ['Masukan resi:', '']  
}
LCD_DATA_TAKING_ITEM = {
    'cmd' : 'keypad',
    'payload' : ['INFO:', '-> SILAKAN AMBIL']  
}
LCD_DATA_AFTER_TAKING_ITEM = {
    'cmd' : 'keypad',
    'payload' : ['INFO:', '-> BRG DIAMBIL!']  
}
LCD_DATA_ERROR_UNIVERSAL_PASSWORD = {
    'cmd' : 'routine',
    'payload' : ['ERROR:', 'Uni pass > 4 c!'] 
}

SOUND_DATA_WARNING_DOOR_OPEN = 'tutup_pintu.wav'
SOUND_DATA_POSE_COURIRER = 'pose_kurir.wav'
SOUND_DATA_TAKING_PICTURE = 'ambil_foto.wav'
SOUND_DATA_PUT_ITEM =  'taruh_paket.wav'
SOUND_DATA_ACCEPTED_ITEM ='diterima.wav'
SOUND_DATA_TAKING_ITEM = 'ambil_barang.wav'
SOUND_DATA_INSTRUCTION_DEL_ITEM = 'instruksi_hapus_item_di_app.wav'

### TIMEOUT
KEYPAD_TIMEOUT = 5 # secs
DOOR_TIMEOUT = 5 #
NETWORK_TIMEOUT = 5

WEIGHT_OFSET = 1.0 # Added for prevent sensor from fluctuation value.


class ThreadOperation:
    def __init__(self) -> None:
        self.queue_data_to_lcd = '' 
        self.temp_storage_data= []    # store data from network   (should build handling function)
        self.initial_data = {}        # concise data from temp_storage_data ('no_resi' : no_index_of_temp_storage)
        self.keypad_buffer = ''
        self.latest_weight = None 
        self.st_msg_has_not_displayed = True
        self.item_is_stored = False
        self.keypad_session_ok =  False
        self.taking_item_ok = False # state for user taking the item inside the box
        # Object class
        self.lock = threading.Lock()
        self.periph = PeripheralOperations()
        self.network = Network()

        self.periph.init_all()


    def set_queue_to_lcd_thread(self, q_to_send):
        self.queue_data_to_lcd = q_to_send


    def _create_payload(self, app_name:str, method, is_data_object = False, **kwargs)-> dict:
        lines = None        
        data_object = {}
        lc_app_name = str.lower(app_name)

        if lc_app_name == 'lcd':
            if is_data_object:
                data_object = {'method' : method }
                payload = {'payload' : kwargs['data_object']}
                data_object.update(payload)
            else:
                lines = [kwargs[key] for key in ['first_line', 'second_line'] \
                        if key in kwargs]
                
                # Raise value error when lines don't have intended params
                len_of_lines = len(lines)
                len_of_params = len(kwargs.values())
                if len_of_lines != 2 or len_of_params != 2:
                    raise ValueError("Lcd parameters should be only 'first_line' and 'second_line'!")
                
                payload = {'payload':lines}
                data_object = {'cmd': method}
                data_object.update(payload)

        if lc_app_name == 'network':
            if is_data_object:
                data_object = {'method' : method }
                payload = {'payload' : kwargs['data_object']}
                data_object.update(payload)
            else:
                data_object = {'method': method}
                data_object.update(kwargs)
            
        return data_object
    

    def _send_data_queue(self, queue_thread: queue.Queue, data : dict):
        with self.lock:
           return "full" if queue_thread.full() else \
            queue_thread.put(data, timeout=1.0)
        

    def _request_data_to_server(self, payload:dict):
        get_response = None
        # all params must be initialized
        status, response = self.network.handle_commands(payload, auth_turn_on=True)
        get_response = response ### should return list contains no_resi
        return status, get_response
    

    def _get_image_as_binary(self, file_name:str):
        photo_path = './assets/photos/' + str(file_name)
        with open(photo_path, 'rb') as f:
            bin_photo = f
        return bin_photo
    

    def _make_initial_data(self, data:list) -> dict:
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
        if data != None: 
            for item in data:
                if not isinstance(item, dict):
                    is_dict = False
            
        # If data is correct, update with new data from server
        if is_dict and data != None:
            for index, data in enumerate(data):
                temp_data_initial = {data['no_resi'] : index }
                data_initial.update(temp_data_initial)

        return data_initial
    

    def get_data_from_config(self, section:str, param:str):
        parser_ver = configparser.ConfigParser()
        parser_ver.read('./conf/config.ini')
        data = parser_ver.get(section, param)
        return data


    def check_universal_password(self, universal_password):
        # universal password should not exceed 4 chars!
        len_pass = len(universal_password)
        if len_pass > 4:
            # send data to lcd
            self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_ERROR_UNIVERSAL_PASSWORD)
            raise ValueError("Universal password should not exceed 4 chars!") 


    def run(self):
        # initially, keypad is not pressed
        keypad_is_pressed = None

        # get universal password
        UNIVERSAL_PASSWORD = self.get_data_from_config('pass', 'universal_password')

        # check uni pass
        self.check_universal_password(UNIVERSAL_PASSWORD)

        # Get data from server
        status_code, self.temp_storage_data = self._request_data_to_server(
            {'method' : 'GET', 'payload' : {'no_resi' : '0'}})
        
        #Make dict object stored no_resi and index of temp_storage_data
        # by doing this, we can match 'no_resi' faster and ease us for sending data to 'success_item' database
        self.initial_data = self._make_initial_data(self.temp_storage_data)

        # Read current weight and store it. It uses for comparing in door session.
        self.latest_weight = self.periph.get_weight()

        # start time for network
        start_time_network = time.time()
                
        while True:
            current_time_network = time.time()
            # Routine task to get data from server
            if current_time_network - start_time_network > NETWORK_TIMEOUT:
                start_time_network = current_time_network
                status_code, self.temp_storage_data = self._request_data_to_server(
                    {'method' : 'GET', 'payload' : {'no_resi' : '0'}})
                self.initial_data = self._make_initial_data(self.temp_storage_data)
                if status_code == 200:
                    self._send_data_queue(self.queue_data_to_lcd, data = LCD_DATA_GET_SUCCESS)
                else:
                    LCD_DATA_GET_FAILS = self._create_payload('lcd', 'routine', False, first_line = "INFO REQUESTS",
                                                               second_line = "Gagal => " + str(status_code))
                    self._send_data_queue(self.queue_data_to_lcd, data = LCD_DATA_GET_FAILS)
                time.sleep(1.0)
                self.st_msg_has_not_displayed = True
                #debug
                print(self.temp_storage_data)

            # display first message once
            if self.st_msg_has_not_displayed:
                self.st_msg_has_not_displayed = False
                self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_ST_MSG)
            
            keypad_is_pressed  = self.periph.read_input_keypad()

            if keypad_is_pressed != None:
                self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_FISRT_INPUT_KEYPAD)
                self.st_msg_has_not_displayed = True
                start_time_keypad_session = time.time()
                # Keypad session start here
                while True:
                    current_time = time.time()
                    keypad_data_input = self.periph.read_input_keypad()
                    #keypad_data_input = str(input('masukan char data: \n'))

                    # timeout function
                    if current_time - start_time_keypad_session > KEYPAD_TIMEOUT:
                        self.st_msg_has_not_displayed = True
                        self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_TIMEOUT)
                        time.sleep(2.0) # visible for user
                        break

                    # read keypad input from user
                    if keypad_data_input != None:
                        self.keypad_buffer = self.keypad_buffer + str(keypad_data_input)
                        data_lcd = self._create_payload('lcd', method= 'keypad', first_line = 'Masukan resi:', second_line = self.keypad_buffer)
                        self._send_data_queue(self.queue_data_to_lcd, data_lcd)
                        
                    # Perform validation when keypad entered 4 times.
                    if len(self.keypad_buffer) == 4:
                        # valid
                        print(f"Keypad buffer : {self.keypad_buffer}")
                        print(f"available resi : {self.initial_data}")
                        # Check with keys in dict (no_resi = keys, index = values)
                        if self.keypad_buffer in self.initial_data.keys():
                            self.keypad_session_ok = True
                            self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_NO_RESI_SUCCESS)
                            break
                        # universal password
                        elif self.keypad_buffer == UNIVERSAL_PASSWORD:
                            self.taking_item_ok = True
                            break
                        else:
                            self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_RESI_FAILED)
                            self.keypad_session_ok = False
                            time.sleep(2.0)
                            break
                
                self.st_msg_has_not_displayed = True

            if self.taking_item_ok:
                self.periph.unlock_door()
                self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_TAKING_ITEM)
                self.periph.play_sound(SOUND_DATA_TAKING_ITEM)

                start_time_door_session = time.time()
                while True:
                    current_time = time.time()
                    door_pos = self.periph.sense_door()

                    if door_pos == 1:
                        break
                    
                    # time out door session
                    if current_time - start_time_door_session > DOOR_TIMEOUT:
                        self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_DOOR_ERROR)
                        self.periph.play_sound(SOUND_DATA_WARNING_DOOR_OPEN)
                        time.sleep(1.0)
                
                self.periph.lock_door()
                self.latest_weight = self.periph.get_weight() # get the latest empty weight
                self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_AFTER_TAKING_ITEM)
                self.periph.play_sound(SOUND_DATA_INSTRUCTION_DEL_ITEM)


            if self.keypad_session_ok:
                self.periph.play_sound(SOUND_DATA_POSE_COURIRER)
                time.sleep(1)
                self.periph.play_sound(SOUND_DATA_TAKING_PICTURE)                
                self.periph.capture_photo()

                time.sleep(0.8)
                self.periph.unlock_door()
                self.periph.play_sound(SOUND_DATA_PUT_ITEM)
                
                # start timer for time out door session
                start_time_door_session = time.time()
                # Door session
                # Door session is when door is open and item should be stored inside device box.
                # read weight will be perform with door sense as indicator for item is stored.
                # no weight change after door is closed means no item stored inside box. So, we need to
                # omit to perform delete no resi data and other stuffs (read: is stored session bellow)
                while True:
                    # update time for this sessiom
                    current_time = time.time()
                
                    read_weight = self.periph.get_weight()
                    door_pos = self.periph.sense_door()
                    #debug

                    #debug
                    print(f" weight: {read_weight}")
                    print(f" door position: {door_pos}")

                    # timeout function
                    # only stop when door is closed
                    if current_time - start_time_door_session > DOOR_TIMEOUT:
                        self.item_is_stored = False 
                        self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_DOOR_ERROR)
                        self.periph.play_sound(SOUND_DATA_WARNING_DOOR_OPEN)
                        time.sleep(0.8)          

                    # Item received
                    if read_weight > self.latest_weight + WEIGHT_OFSET and door_pos == 1:
                        self.item_is_stored = True
                        # update latest weight when item is stored
                        self.latest_weight = read_weight 
                        break

                    #only door is closed (no item received)
                    elif read_weight < self.latest_weight + WEIGHT_OFSET and door_pos == 1:
                        self.item_is_stored = False
                        self.periph.lock_door()
                        self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_NO_ITEM_RECEIVED)
                        time.sleep(2.0) # visible for human
                        break

                self.st_msg_has_not_displayed = True
                # whatever the situation occured, after the door is closed, lock the door!
                self.periph.lock_door()
                
                # Final session
                # Final session where device performs delete method in table 'items' inside database (
                # indicate the items is stored) and post data to table 'success_items' in database (afterward
                # it will be used with another end device.
                if self.item_is_stored:
                    # send data to output peripherals
                    self._send_data_queue(self.queue_data_to_lcd, LCD_DATA_THANKYOU) 
                    self.periph.play_sound(SOUND_DATA_ACCEPTED_ITEM)
                    
                    # get first name from first file in directory
                    photo_file_name = self.periph.get_photo_name()[0]
                    print(f"Foto name: {photo_file_name}")

                    # sending photo has to be in binary file of photo
                    last_foto_path = "./assets/photos/" + photo_file_name
                    with open(last_foto_path, 'rb') as f:
                        bin_photo = f.read()

                    #create photo payload with param 'photo' and value are file name and photo bin.
                    # it will send data in FILES not in data body.
                    payload_photo = {'photo' : (photo_file_name, bin_photo)}
                    
                    #delete the stored item.
                    status_code, resp = self._request_data_to_server({'method' : 'DELETE', 'payload' : {'no_resi' : self.keypad_buffer}})
                    
                    print(f"response from server [DELETE]: {resp}")
                    print(f"keypad buffer : {self.keypad_buffer}")

                    # Post data to table 'success_items'.
                    # Get data stored in this session.
                    index = self.initial_data[self.keypad_buffer]
                    payload = self.temp_storage_data[index]
                    # added payload photo
                    payload.update(payload_photo)
                    # create full payload for success_item API            
                    payload_success_item = self._create_payload('network', method='success_items', is_data_object = True, data_object = payload)
                    # send request to success_items API.
                    status_code, response = self._request_data_to_server(payload_success_item)
                    print(response)     
                    # Display the first message in LCD.           
                    self.st_msg_has_not_displayed = True
             
            ## clean all
            self.keypad_buffer = ''
            self.keypad_session_ok = False
            self.item_is_stored = None
            self.taking_item_ok = None
            # Delete photos in local storage.
            if self.periph.get_photo_name() is not None:
                self.periph.delete_photo()
                
            