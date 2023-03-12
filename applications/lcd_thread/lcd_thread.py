'''
    File           : lcd_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
        This code helps to create an thread for lcd operation. It can read queue data (mutex),
    perform routine operation for LCD (printing items stored in box and waiting of items),
    and handling keypad operation.

        Since this code needs to access several mutex data, we have to put threading.Lock to avoid
    race condition between thread. 
    
        The driver of this code is 'run' method. It has 2 flows, the first is printing items stored and item waiting, 
    and the second is keypad handling. It is determined by keypad_flag list. keypad_flag is 0 means 
    the first flow is used and keypad_flag is 1 means the second flow is used.

        Attributes:
            dev_addr (hex)                  : Device i2c address (eg. 0x27)
            bus_addr (int)                  : Bus address used in i2c.
            buffer_no_resi_data (str)       : Buffer for 4 digits resi numbs in keypad_handling method.
            queue_data_read (queue.Queue)   : Data contain first and second data to displayed. Content must be string and max is 2 itms
            keypad_flag (list)              : Flag for determining go to mode keypad handling.
            queue_keypad_char (queue.Queue) : Buffer for a char that will be displayed in LCD when keypad handling method invoked.

    NOTE: It must declared in function if it as a threading and invode run method .eg.
        """
            def thread_lcd_func():
                lcd_t = LcdThread(
                    args
                )
                lcd_t.run()
        """

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
            keypad_char_data: queue.Queue
    ):
        self._dev_addr = dev_addr
        self._bus_addr = bus_addr
        self._buffer_no_resi_data = EMPTY_STRING
        self._queue_data_read = queue_data_read
        self._keypad_flag = keypad_flag  # content should be 0 or 1 (interger)
        self._queue_keypad_char = keypad_char_data
        # check data type
        if not isinstance(self._keypad_flag[0], int) and \
            not isinstance(self._queue_keypad_char, queue.Queue):
            raise ValueError(
                "Keypad flag or keypad char data should be list data type!")
        self._lcd = Lcd(self._dev_addr, self._bus_addr)
        self._lcd.init_lcd()
        time.sleep(2)
        self._lcd.write_text(0, 'Selamat Datang')
        self._lock = threading.Lock()

    def read_queue_data(self):
        with self._lock:
            return EMPTY_STRING if self._queue_data_read.empty() \
                else self._queue_data_read.get()

    def parse_data(self, data: list):
        first_line = data[0]
        second_line = data[1]
        return first_line, second_line

    def get_keypad_flag(self):
        with self._lock:
            return self._keypad_flag[0]

    def get_keypad_char_data(self):
        with self._lock:
            return EMPTY_STRING if self._queue_keypad_char.empty() \
                else self._queue_keypad_char.get()
        
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
        # handling exceeded input data and clear no resi buff.
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
            self._lcd.write_text(0, f"{first_line}")
            self._lcd.write_text(1, f"{second_line}")
            time.sleep(1.5)

    def run(self):
        # check data from queue
        data_display = self.read_queue_data()
        # check if keypad is entered
        is_keypad_flag = self.get_keypad_flag()
        if is_keypad_flag:
            self.keypad_handling()
        # check if items data is available
        if len(data_display) != 0 and is_keypad_flag != 1:
            item_stored, item_waiting = self.parse_data(data_display)
            self._lcd.clear_lcd()
            self._lcd.write_text(0, f'Itms stored : {item_stored}')
            self._lcd.write_text(1, f'Itms waiting: {item_waiting}')
