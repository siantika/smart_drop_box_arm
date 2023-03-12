'''
    File           : lcd_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
        This code helps to create an thread for lcd operation. It can read queue data (mutex),
    perform routine operation for LCD (printing items stored in box and waiting of items),
    and handling keypad operation.

        Since this code needs to access several mutex data, we have to put threading.Lock to avoid
    race condition between thread. in fact, lcd data is used by 2 threads (operation thread and 
    network thread) and the keypad flag shared-variable.
    
    Dependencies (not built in module):
        + lcd.py --> driver for LCD 16x2 i2c 

    License: see 'licenses.txt' file in the root of project
'''
import queue
import sys
import time
import threading
sys.path.append('drivers/lcd')
from lcd import Lcd

EMPTY_STRING = ""
NO_RESI_MAX_LENGTH = 4

class LcdThread:
    def __init__(
            self,
            dev_addr,
            bus_addr,
            queue_data_read: queue.Queue,
            keypad_flag: list,
            keypad_char_data: list
    ):
        self._dev_addr = dev_addr
        self._bus_addr = bus_addr
        self._buffer_no_resi_data = EMPTY_STRING
        self._queue_data_read = queue_data_read
        self._keypad_flag = keypad_flag  # content should be 0 or 1 (interger)
        self._keypad_char_data = keypad_char_data
        # check data type
        if not isinstance(self._keypad_flag[0], int) and not isinstance(self._keypad_char_data[0], str):
            raise ValueError(
                "Keypad flag or keypad char data should be list data type!")
        self._lcd = Lcd(self._dev_addr, self._bus_addr)
        self._lcd.init_lcd()
        self._lock = threading.Lock()

    def read_queue_data(self):
        with self._lock:
            if not self._queue_data_read.empty():
                read_data = self._queue_data_read.get()
        return read_data

    def parse_data(self, data: list):
        first_line = data[0]
        second_line = data[1]
        return first_line, second_line

    def get_keypad_flag(self):
        with self._lock:
            return self._keypad_flag[0]

    def get_keypad_char_data(self):
        with self._lock:
            return self._keypad_char_data[0]

    def keypad_handling(self):
        # get char data
        char_data = self.get_keypad_char_data()
        # contains message for successfuly inserted correct no resi
        data_display = self.read_queue_data()
        no_resi_buff_length = len(self._buffer_no_resi_data)
        if char_data is not EMPTY_STRING and no_resi_buff_length <= NO_RESI_MAX_LENGTH:
            self._lcd.clear_lcd()
            self._lcd.write_text(0, 'Masukan No Resi:')
            self._buffer_no_resi_data += char_data
            self._lcd.write_text(1, self._buffer_no_resi_data)
        # handling exceeded input data adn clear no resi buff.
        if no_resi_buff_length > NO_RESI_MAX_LENGTH:
            self._buffer_no_resi_data = EMPTY_STRING
            self._lcd.clear_lcd()
            self._lcd.write_text(0, "No resi lebih")
            self._lcd.write_text(1, "dari 4 digit!")
        # check data_display is exist
        if len(data_display) != 0:
            first_line, second_line = self.parse_data(data_display)
            self._buffer_no_resi_data = EMPTY_STRING
            self._lcd.clear_lcd()
            self._lcd.write_text(0, f'{first_line}')
            self._lcd.write_text(1, f'{second_line}')
            time.sleep(1.5)

    def run(self):
        # check data from queue
        data_display = self.read_queue_data()
        # check if keypad is entered
        is_keypad_flag = self.get_keypad_flag()
        if is_keypad_flag:
            self.keypad_handling()
        # check if items data is available
        if data_display != 0 and is_keypad_flag != 1:
            item_stored, item_waiting = self.parse_data(data_display)
            self._lcd.clear_lcd()
            self._lcd.write_text(0, f'Itms stored : {item_stored}')
            self._lcd.write_text(1, f'Itms waiting: {item_waiting}')
