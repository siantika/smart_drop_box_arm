'''
    25/02/2023
    NOTE:
        + Still need to find mock methods for threading (I used patcher, still doesn't work).
          Try to mock threading using strategy like mock_wiringpi !.
        + Write test code for clear _buffer_no_resi_data after 4 times called!


'''

from unittest.mock import patch, call
import sys
sys.path.append('applications/lcd_thread')
sys.path.append('drivers/lcd')

from lcd_thread import LcdThread
from lcd import Lcd

class TestLcdThread:

    def help_mock_lcd_methods(self):
        self.patcher1 = patch('lcd.Lcd.init_lcd')
        self.patcher2 = patch('lcd.Lcd.write_text')
        self.patcher3 = patch('lcd.Lcd.clear_lcd')
        self.patcher4 = patch('lcd.Lcd.__init__')
        

        self.mock_lcd_init_lcd = self.patcher1.start()
        self.mock_lcd_write_text = self.patcher2.start()
        self.mock_lcd_clear_lcd = self.patcher3.start()
        self.mock_lcd = self.patcher4.start()
        
        self.mock_lcd.return_value = None

    def help_mock_time_methods(self):
        patcher1 = patch('time.sleep')
        self.mock_time_sleep = patcher1.start()

    def stop_mocks(self):
        patch.stopall()
        


    def test_init_process_should_be_correct(self):
        '''
            Tests:
                1. Should create an object from LCD with dev_addr = 0x27
                   and BUS_I2C = 0
                2. Should call lcd.init_lcd() once
        '''
        self.help_mock_lcd_methods()
        lcd_thread = LcdThread(0x27, 0)

        assert lcd_thread._dev_addr == 0x27
        assert lcd_thread._bus_addr == 0
        assert isinstance(lcd_thread._lcd, Lcd)
        assert lcd_thread._buffer_no_resi_data == ''
        self.mock_lcd.assert_called_once_with(0x27, 0)
        self.mock_lcd_init_lcd.assert_called_once()
        
        self.stop_mocks()

        

    def test_read_new_queue_data_should_be_correct(self):
        '''
            Tests:
                1. should read queue value as parameter (queue is not empty)
                2. should store data in local variable (_data_lcd)
                3. should not contain word "network" and return empty string

        '''

        self.help_mock_lcd_methods()
        
        lcd_thread = LcdThread(0x27, 0)

        lcd_thread.read_queue_data('NO DATA')

        assert lcd_thread._new_data_from_queue == 'NO DATA' 
        assert lcd_thread._data_lcd == 'NO DATA'

        #should not contain word "network" and return empty string
        lcd_thread.read_queue_data('Network: added 1 item')
        assert lcd_thread._data_lcd == 'NO DATA'

    def test_read_new_queue_data_network_should_be_correct(self):
        '''
            Tests:
                1. should read queue data network value as parameter (queue is not empty)
                2. should store data in local variable (_data_lcd)

        '''

        self.help_mock_lcd_methods()
        
        lcd_thread = LcdThread(0x27, 0)

        lcd_thread.read_queue_data('Network: 1 items added')

        assert lcd_thread._network_data ==' 1 items added'

    def test_routine_lcd_operation_should_be_correct(self):
        self.help_mock_lcd_methods()
        self.help_mock_time_methods()
        lcd_thread = LcdThread(0x27, 0)

        lcd_thread.routine_operation()

        self.mock_lcd_clear_lcd.assert_called()
        self.mock_lcd_write_text.assert_has_calls(
            [
                call(0, 'Items stored: '),
                call(1, '2 Items'),
                call(0, 'Smart Drop Box'),
                call(1, 'Version 1.0')
            ]
        )
        self.mock_time_sleep.assert_has_calls(
            [
                call(2),
                call(2),
            ]
        )
        self.stop_mocks()
    

    def test_keypad_handling_arguments_in_lcd_should_be_correct(self):
        '''
            get new data from queue keypad, print that data 
        '''
        self.help_mock_lcd_methods()
        self.help_mock_time_methods()

        lcd_thread = LcdThread(0, 0x27)

        lcd_thread.keypad_handling(1, '8')

        assert lcd_thread._keypad_flag == 1
        assert lcd_thread._queue_keypad_data ==  '8'
        assert isinstance(lcd_thread._queue_keypad_data, str)
        assert lcd_thread._keypad_status_operation_flag == None
        
        ### test _queue keypad data variable should convert
        lcd_thread.keypad_handling(1, 8)
        assert isinstance(lcd_thread._queue_keypad_data, str)

        self.stop_mocks()

    def test_keypad_handling_should_print_data_correctly(self):
        self.help_mock_lcd_methods()

        lcd_thread = LcdThread(0x27, 0)

        lcd_thread.keypad_handling(1, '8')
        lcd_thread.keypad_handling(1, '9')
        lcd_thread.keypad_handling(1, '2')
        lcd_thread.keypad_handling(1, '1')

        self.mock_lcd_clear_lcd.assert_called()
        self.mock_lcd_write_text.assert_has_calls(
            [
                call(0, 'Masukan No Resi:'),
                call(1, '8'),
                call(0, 'Masukan No Resi:'),
                call(1, '89'),
                call(0, 'Masukan No Resi:'),
                call(1, '892'),
                call(0, 'Masukan No Resi:'),
                call(1, '8921'),
            ]
        )
        self.stop_mocks()

    def test_keypad_handling_should_print_data_no_more_than_4_resi_number(self):
        self.help_mock_lcd_methods()

        lcd_thread = LcdThread(0x27, 0)

        '''
            No resi should not exceed 4 numbs ! or raise an error (ValueError)!
        '''
        try:    
            lcd_thread.keypad_handling(1, '8')
            lcd_thread.keypad_handling(1, '9')
            lcd_thread.keypad_handling(1, '2')
            lcd_thread.keypad_handling(1, '1')
            lcd_thread.keypad_handling(1, '5')
        except ValueError as ve:
            assert str(ve) == 'resi number is more than 4 numbs!'
        else:
            assert False



    def test_keypad_handling_status_operation_is_true(self):
        self.help_mock_lcd_methods()
        self.help_mock_time_methods()

        lcd_thread = LcdThread(0x27, 0)
        lcd_thread.keypad_handling(1, '', 'true')

        assert lcd_thread._keypad_status_operation_flag == 'true'
        self.mock_lcd_clear_lcd.assert_called()
        self.mock_lcd_write_text.assert_called_once_with(0,'    Benar !')
        self.mock_time_sleep(2)


    def test_keypad_handling_status_operation_is_false(self):
        self.help_mock_lcd_methods()
        self.help_mock_time_methods()

        lcd_thread = LcdThread(0x27, 0)
        lcd_thread.keypad_handling(1, '', 'false')

        assert lcd_thread._keypad_status_operation_flag == 'false'
        self.mock_lcd_clear_lcd.assert_called()
        self.mock_lcd_write_text.assert_called_once_with(0,'No Resi Salah !')
        self.mock_time_sleep(2)
        assert lcd_thread._buffer_no_resi_data == ''

  