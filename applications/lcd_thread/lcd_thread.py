'''
    File           : lcd_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
        This code helps to create an thread for lcd operation. It can read queue data (mutex),
    perform routine operation for LCD (printing Items stored in box, and software version),
    and handling keypad operation.

        Since this code needs to access several mutex data, we have to put threading.Lock to avoid
    race condition between thread. in fact, lcd data is used by 2 threads (operation thread and network thread)
    and the flags variables.
    
    Dependencies (not built in module):
        + lcd.py --> driver for LCD 16x2 i2c 

    License: see 'licenses.txt' file in the root of project

   

'''
import threading
import time
import sys
sys.path.append('drivers/lcd')
from lcd import Lcd

class LcdThread:
    def __init__(self, dev_addr, bus_addr):
        self._dev_addr = dev_addr
        self._bus_addr = bus_addr
        self._lcd = Lcd(self._dev_addr, self._bus_addr)
        self._lcd.init_lcd()
        self._lock = threading.Lock()
        self._buffer_no_resi_data = ''

    '''
        Desc    : when queue data contains 'Network' word, it will store in 
                _network_data (_data_lcd still hold old data) 
    '''
    def read_queue_data(self, queue_lcd_data):
        '''
            lock the process because it reads Mutex data
        '''
        self._lock.acquire()
        self._new_data_from_queue = queue_lcd_data
        self._lock.release()

        splited_data = self._new_data_from_queue.split(':')
        _flag_network = 0 

        for word in splited_data:
            if 'Network' in word:
                self._network_data = splited_data[1]
                _flag_network = 1

        if not _flag_network:
            self._data_lcd = self._new_data_from_queue
        
    
    def routine_operation(self):
        self._lcd.clear_lcd()
        self._lcd.write_text(0,'Items stored: ')
        self._lcd.write_text(1, '2 Items')
        time.sleep(2)
        self._lcd.clear_lcd()
        self._lcd.write_text(0,'Smart Drop Box')
        self._lcd.write_text(1, 'Version 1.0')
        time.sleep(2)

    '''
        Desc: This function helps to handling keypad operation from thread_operational.
              It is trigerred by self._keypad_flag argument (value = 1). It will print
              char by char in line no 2 (LCD row) from data that sent by another thread.
              It will print status operational in LCD in concern of _keypad_status_operation_flag
              (this argument is controlled by another thread).
              To exiting this function, we have to give keypad_flag argument with 0.

        Param : @keypad_flag -> trigered the operation keypad_handling function.
                @queue_keypad_data -> store input pin from user. The data will be printed in LCD 
                                        (First Input First Output style).
                @keypad_status_operation_flag ->  It prints data according validation result in another thread
                                                  [true, false, None]
    
    '''
    def keypad_handling(self, keypad_flag, queue_keypad_data : str, keypad_status_operation_flag = None):
        self._lock.acquire()
        self._keypad_flag = keypad_flag
        self._queue_keypad_data = str(queue_keypad_data)
        self._keypad_status_operation_flag = keypad_status_operation_flag
        self._lock.release()
        
        if self._keypad_flag:            
            if self._queue_keypad_data != '':
                self._lcd.clear_lcd()
                self._lcd.write_text(0, 'Masukan No Resi:')   
                self._buffer_no_resi_data += self._queue_keypad_data
                self._lcd.write_text(1, self._buffer_no_resi_data)

                if len(self._buffer_no_resi_data) > 4:
                    raise ValueError('resi number is more than 4 numbs!')
        
            if self._keypad_status_operation_flag == 'true':
                self._lcd.clear_lcd()
                self._lcd.clear_lcd()
                self._lcd.write_text(0,'    Benar !')
                time.sleep(2)
                self._lcd.clear_lcd()
            
            elif self._keypad_status_operation_flag == 'false':
                self._lcd.clear_lcd()
                self._lcd.write_text(0,'No Resi Salah !')
                time.sleep(2)
                self._buffer_no_resi_data = '' 

            

    
    
