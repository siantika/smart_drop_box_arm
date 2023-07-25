'''
    File           : Display app
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 
    
        This code helps for creating a thread for display app. It will print data
    if queue_data_read attribute is exist with correct data ({'cmd': DisplayMode.NORMAL, 
    'payload':[firstline_data, secondline_data]}) else it will print the latest data 
    obtained from queue_data_read attribute.
        Attributes:
            queue_data_read (mp.Queue)  : Queue data for reading payload
                                          from other thread.
                                          Queue data content is a dict objec.
                                          eg. {'cmd': 'normal', 
                                          'payload': [firstline_data, secondline_data]}
            _Display                     : Display object

    NOTE: This code is intended for multiprocessing style. 
          Here is the code should be put in the main code (thread creation):
        """
            def thread_lcd_func():
                lcd_t = LcdThread(
                    args
                )
                lcd_t.run()
        """

    Dependencies:
        + lcd.py --> driver for LCD 16x2 i2c (Now)

'''
import multiprocessing as mp
import os
import sys
from enum import Enum, auto

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir,'drivers/lcd'))
sys.path.append(os.path.join(parent_dir,'utils'))

# Using LCD 16 x 2 with I2C protocol
from lcd import LcdI2C
from Interfaces import AppInterface

# Make sure your LCD hardware address and spi's bus are correct !
DEV_ADDR = 0x27
DEV_BUS = 0


class DisplayMode(Enum):
    """ Enumeration of Display mode.
    It affects the way of Display printing data.
    (running text, normal, etc)
        Currently, it only has normal mode.
    """
    NORMAL = auto()


class DisplayApp(AppInterface):
    '''
        This class is used for creating a display app.
            Attribs:
            _queue_data_read (mp.Queue) : Variable that stored data from
                                          other queue (set queue)
            _display (LcdI2C) : Lcd Object : Performing lcd basic operations
                                         with I2C protocol
    '''
    def __init__(self)-> None:
        """ Initiates queue data and display object 
            By now, we use lcd 16 x 2 i2c for display.
        """
        self._queue_data_read = mp.Queue()
        self._display = LcdI2C(DEV_ADDR, DEV_BUS)
        self._display.init_lcd()

    def _read_queue_data(self)-> mp.Queue:
        '''
            Read queue data from shared resource. 
            It uses block mechanism, so this method
            will block the next process until it fed by data from other 
            thread.
            By doing this, we saving the CPU usage.

            Returns:
                payload data from other thread. Data type of queue data
                is a dict.

        '''
        return self._queue_data_read.get()

    def set_queue_data(self, queue_data :mp.Queue):
        '''
            Set queue data from other thread.
            User should invoke this function.
        '''
        self._queue_data_read = queue_data

    def _parse_dict_data(self, data: dict)-> tuple:
        '''
            Parsing dictionary data becoming 2 items (tuple).
            first data in dict contains command for LCD, the other one 
            contains payload (data to be displayed on lcd)
            Raises:
                ValueError  : if contents in payload are not string.
            
            Returns:
                cmd and text data in tuple. Text data contains list 
                of string data.
        '''
        cmd  = data['cmd']
        data_text = data['payload']
        # Payload content should be string type
        if not all(isinstance(item, str) for item in data_text):
            raise ValueError("Payload contents should be string!")
        return cmd, data_text

    def _normal_print(self, first_line:str, second_line:str)-> None:
        """ Just print data to LCD (no running text, etc) """
        self._display.clear_lcd()
        self._display.write_text(0, first_line)
        self._display.write_text(1, second_line)

    def _print_data(self)-> None:
        '''
            Controls behaviours of lcd task.
            It reads data from shared queue. While no data in 
            shared queue, it stays in read queue data function
            (Not continue to next operation)      
        '''
        # Read queue data from control thread
        queue_data = self._read_queue_data()
        cmd, display_data = self._parse_dict_data(queue_data)
        mode = DisplayMode[cmd]
        if mode is DisplayMode.NORMAL:
            self._normal_print(display_data[0], display_data[1])            

    def run(self)->None:
        '''
            Driver method for running the task in infinite loop.
        '''
        while True:
            self._print_data()
    