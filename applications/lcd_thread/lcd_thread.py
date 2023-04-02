'''
    File           : lcd_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 
    
        This code helps to create an thread for lcd operation. It will print data
    if queue_data_read attribute is exist with correct data ({'cmd': 'routine' or 
    'keypad', 'payload'=[firstline_data, secondline_data]}) else it will print the 
    lastest data from queue_data_read attribute.
    
        Since this code needs to access shared resource (queue_data_read attribute), 
    we have to put threading.Lock to avoid race condition between threads. 
    
        Attributes:
            queue_data_read (mp.Queue)  : Queue data to read from other thread.
                                             Queue data content is dict objec.
                                             eg. {'cmd': 'routine' or 'keypad', 
                                            'payload'=[firstline_data, secondline_data]}
            _lcd (lcd.Lcd)                 : Lcd object from lcd driver. It uses to operate
                                             LCD 16x2 I2C.
            _lock (threading.Lock)         : lock object from threading.Lock. It uses for 
                                             mutex operations.

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
import multiprocessing as mp
import configparser
import os
import sys
import threading

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir,'drivers/lcd'))

full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')

from lcd import Lcd

DEV_ADDR = 0x27
DEV_BUS = 0

class LcdThread:
    '''
        This class is used for create a LCD thread.
    
    '''
    def __init__(self)-> None:
        self.queue_data_read = ''
        self._lcd = Lcd(DEV_ADDR, DEV_BUS)
        self._lock = threading.Lock()
        self._lcd.init_lcd()
        self._welcome_display()


    def _welcome_display(self)->None:
        '''
            Printing device version in LCD
        '''
        version = self._get_device_version()
        self._lcd.write_text(0, "*Smart Drop Box*")
        self._lcd.write_text(1, f"----{version}----") # version content must contains 8 chars


    def _get_device_version(self)-> str:
        '''
            Get device version from config.ini file. It will print error info in lcd if
            version chars exceeds 8 chars.

            Raises  : 
                    Inheritance error handling from configparser class.
                    ValueError : when version's length exceeds 8 chars and assigned None/empty.

            Return  : 
                    device_version (str) : device version in max. 8 chars 

        '''
        parser_ver = configparser.ConfigParser()
        parser_ver.read(full_path_config_file)
        device_version = parser_ver.get('version', 'dev_version')
        len_dev_ver = len(device_version)

        if len_dev_ver > 8 or len_dev_ver == 0:
            self._lcd.write_text(0, 'Error Info:')
            self._lcd.write_text(1, 'Check Ver str!')
            raise ValueError ("Version's length should not exceeded 8 chars or empty!")
        return device_version


    def read_queue_data(self)-> mp.Queue:
        '''
            Read queue from shared resource. It uses lock method to prevent race
            conditions between threads accessing the same resource.

            Returns:
                the queue data if exists, else return None.

        '''
        # if not isinstance(self.queue_data_read, type(mp.Queue)):
        #     raise AttributeError('queue_data_read attribute had not been setted!')
        with self._lock:
            return None if self.queue_data_read.empty() \
                else self.queue_data_read.get(timeout=1)


    def set_queue_data(self, queue_data :mp.Queue):
        '''
            Set queue data from shared resource to be read.
        '''
        self.queue_data_read = queue_data


    def parse_dict_data(self, data: dict)-> tuple:
        '''
            Parsing dictionary data to be 2 items of a tuple.
            first data in dict contains command for LCD, the other one contains payload
            (first line and second line data that will be displayed in LCD).

            Raises:
                ValueError  : if content in payload are not string.
            
            Returns:
                cmd and data_text in tuple. data_text contains list of string data
        '''
        cmd  = data['cmd']
        data_text = data['payload']
        # Payload content should string
        if not all(isinstance(item, str) for item in data_text):
            raise ValueError("Payload contents should be string!")

        return cmd, data_text

    def print_data(self)-> None:
        '''
            Function that handle all the need of lcd tasks.
                    
        '''
        # default value:
        cmd = None
        # read queue data from thread opt
        queue_data = self.read_queue_data()
        #if queue data exist, parse it
        if queue_data is not None:
            cmd, display_data = self.parse_dict_data(queue_data)
        # print data to lcd if cmds are match
        if cmd in ('routine', 'keypad'):
            first_line   = display_data[0]
            second_line = display_data[1]
            self._lcd.clear_lcd()
            self._lcd.write_text(0, first_line)
            self._lcd.write_text(1, second_line)


    def run(self)->None:
        '''
            Driver function to run the task in inifinity looping 
        '''
        while True:
            self.print_data()
    