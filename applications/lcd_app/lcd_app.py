'''
    File           : lcd_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 
    
        This code helps for creating a thread for lcd operation. It will print data
    if queue_data_read attribute is exist with correct data ({'cmd': LcdMode.NORMAL, 
    'payload':[firstline_data, secondline_data]}) else it will print the latest data 
    obtained from queue_data_read attribute.
        
        Attributes:
            queue_data_read (mp.Queue)  : Queue data for reading payload
                                          from other thread.
                                          Queue data content is a dict objec.
                                          eg. {'cmd': 'normal', 
                                          'payload': [firstline_data, secondline_data]}
            _lcd (lcd.Lcd)              : Lcd object from lcd driver. It uses for operating
                                          LCD 16x2 I2C.

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
        + lcd.py --> driver for LCD 16x2 i2c 

'''
import multiprocessing as mp
import os
import sys
from enum import Enum, auto

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir,'drivers/lcd'))

# Using LCD 16 x 2 with I2C protocol
from lcd import LcdI2C

# Make sure your LCD hardware address and spi's bus are correct !
DEV_ADDR = 0x27
DEV_BUS = 0


class LcdMode(Enum):
    """ Enumeration of LCD mode.
    It affects the way of LCD printing data.
    (running text, normal, etc)
        Currently, it only has normal mode.
    """
    NORMAL = auto()

class LcdApp:
    '''
        This class is used for creating a LCD thread.
            Attribs:
            _queue_data_read (mp.Queue) : Variable stored data from
                                          other queue (set queue)
            _lcd (LcdI2C) : Lcd Object : Performing lcd basic operations
                                         with I2C protocol
    '''
    def __init__(self)-> None:
        self._queue_data_read = mp.Queue()
        self._lcd = LcdI2C(DEV_ADDR, DEV_BUS)
        self._lcd.init_lcd()

    def _read_queue_data(self)-> mp.Queue:
        '''
            Read queue from shared resource. It uses block mechanism, so this method
            will wait if no new data in queue (shared resource). Saving CPU usage.

            Returns:
                payload data from thread operation. The data type is dict

        '''
        if self._queue_data_read is None:
            raise AttributeError("queue_data_read \
                                 attribute had not been \
                                 setted!")
        return self._queue_data_read.get()

    def set_queue_data(self, queue_data :mp.Queue):
        '''
            Set queue data from shared resource.
            User should invoke this function.
        '''
        self._queue_data_read = queue_data


    def _parse_dict_data(self, data: dict)-> tuple:
        '''
            Parsing dictionary data to become 2 items of a tuple.
            first data in dict contains command for LCD, the other one contains payload
            (first line and second line data that will be displayed in LCD).

            Raises:
                ValueError  : if content in payload is not string.
            
            Returns:
                cmd and data_text in tuple. data_text contains list of string data
        '''
        cmd  = data['cmd']
        data_text = data['payload']
        # Payload content should be string type
        if not all(isinstance(item, str) for item in data_text):
            raise ValueError("Payload contents should be string!")
        return cmd, data_text

    def _normal_print(self, first_line:str, second_line:str)-> None:
        """ Just print data to LCD (no running text, etc) """
        self._lcd.clear_lcd()
        self._lcd.write_text(0, first_line)
        self._lcd.write_text(1, second_line)

    def _print_data(self)-> None:
        '''
            Function that control behaviours of lcd task.
            It reads data from shared queue. While no data in 
            shared queue, it stays in read queue data function
            (Not continue to next operation)      
        '''
        # read queue data from control thread
        queue_data = self._read_queue_data()
        cmd, display_data = self._parse_dict_data(queue_data)
        mode = LcdMode[cmd]
        if mode is LcdMode.NORMAL:
            self._normal_print(display_data[0], display_data[1])            

    def run(self)->None:
        '''
            Driver function to running the task in infinite loop 
        '''
        while True:
            self._print_data()
    