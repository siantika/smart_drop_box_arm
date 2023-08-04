""" Tests functionalities of Lcd I2C used in 
    display app.
"""

import sys
import multiprocessing as mp
import time
import pytest
from unittest.mock import patch, call
import os
import pytest 

parrent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parrent_dir, 'src/applications/display_app'))
                
sys.path.append('drivers/lcd')
from display_app import DisplayApp, DisplayMode
from lcd import LcdI2C as Lcd

""" Unit tests """
class TestInitMethod:
    def test_init_method_should_has_correct_attribute(self):
        with patch.object(Lcd, '__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd:
            mock_lcd.return_value = None
            lcd_t = DisplayApp()
            assert hasattr(lcd_t, '_queue_data_read')
            assert isinstance(lcd_t._queue_data_read, type(mp.Queue()))


    def test_should_invoke_with_correct_methods(self):
        with patch.object(Lcd, '__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd:
            mock_lcd.return_value = None
            lcd_t = DisplayApp()
            mock_lcd.assert_called_once_with(0x27,0)
            mock_init_lcd.assert_called_once()


class TestSetQueueData:
    def test_set_queue_data_to_read_should_be_correct(self):
        with patch.object(Lcd, '__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd'), \
                patch.object(Lcd, 'write_text'):
            mock_lcd.return_value = None
            test_data = mp.Queue(5)
            lcd_t = DisplayApp()
            lcd_t.set_queue_data(test_data)
            assert lcd_t._queue_data_read == test_data
            assert isinstance(lcd_t._queue_data_read, type(mp.Queue()))

class TestReadQueueData:
    def _help_mock_lcd_driver(self):
        self.mock_lcd_init       = patch.object(Lcd, '__init__').start()
        self.mock_lcd_init_lcd   = patch.object(Lcd, 'init_lcd').start()
        self.mock_lcd_write_text = patch.object(Lcd, 'write_text').start()
        # should return None
        self.mock_lcd_init.return_value = None
    
    def stop_all_patch(self):
        patch.stopall()

    def test_with_not_setted_read_queue_data(self):
        """ Should raise an Attribute error """
        self._help_mock_lcd_driver()
        with pytest.raises(AttributeError):
            lcd_t = DisplayApp()
            lcd_t._queue_data_read = None
            lcd_t._read_queue_data()
        self.stop_all_patch()

    def test_read_queue_data_attribute_error(self):
        self._help_mock_lcd_driver()
        lcd_t = DisplayApp()
        # Make sure _queue_data_read is None to raise AttributeError
        lcd_t._queue_data_read = None
        # When _queue_data_read is None, an AttributeError should be raised
        with pytest.raises(AttributeError):
            lcd_t._read_queue_data()

    def test_with_correct_data(self):
        """ Should retruns inputted data """
        self._help_mock_lcd_driver()
        q_data = mp.Queue(2)
        q_data.put({
            "cmd"     : "routine",
            "payload" : ["Masukan no resi:", "0596"]
            }
        )
        lcd_t = DisplayApp()
        lcd_t.set_queue_data(q_data)
        ret = lcd_t._read_queue_data()
        
        assert ret ==  {
            "cmd"     : "routine",
            "payload" : ["Masukan no resi:", "0596"]
        }
        self.stop_all_patch()

    def test_with_empty_data(self):
        """ Should waiting the data /block others operation"""
        empty_queue = mp.Queue(2)
        # Create a thread that sends data to empty_queue 
        # 5 secs after _read_queue_data is executed.
        # In real scenario, it should wait until data from
        # queue is arrived.
        def put_data_to_queue(queue_data:mp.Queue):
            time.sleep(5)
            queue_data.put({
            "cmd"     : "routine",
            "payload" : ["Masukan no resi:", "0596"]
                 }, timeout = 1
            )
        process_put_data = mp.Process(target=put_data_to_queue, 
                                      args=(empty_queue,))
        self._help_mock_lcd_driver()
        lcd_t = DisplayApp()
        lcd_t.set_queue_data(empty_queue)
        process_put_data.start()
        lcd_t._read_queue_data()
        process_put_data.join()


class TestParseData:
    def test_with_correct_data(self):
        with patch.object(Lcd, '__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd'):
            mock_lcd.return_value = None
            lcd_t = DisplayApp()
            test_data = {"cmd":"NORMAL", "payload":["", "a" ]}
            ret = lcd_t._parse_dict_data(test_data)
            cmd  = DisplayMode[ret[0]]
            data_text = ret[1]
            assert cmd in DisplayMode
            assert data_text == ["", "a"]

    def test_with_wrong_data_format(self):
        with pytest.raises(ValueError):
            with patch.object(Lcd,'__init__') as mock_lcd, \
                patch.object(Lcd, 'init_lcd'):
                mock_lcd.return_value = None
                lcd_t = DisplayApp()
                test_data = {"cmd":"NORMAL", "payload":[5, '4']}
                lcd_t._parse_dict_data(test_data)


""" Integration test"""
class TestDriverClass:
    """ It tested _print_data method since 
        run method invokes _print_data method.
     """
    def _help_mock_lcd_driver(self):
        self.mock_lcd_init       = patch.object(Lcd, '__init__').start()
        self.mock_lcd_init_lcd   = patch.object(Lcd, 'init_lcd').start()
        self.mock_lcd_write_text = patch.object(Lcd, 'write_text').start()
        self.mock_lcd_clear_lcd  = patch.object(Lcd, 'clear_lcd').start()
        # should return None
        self.mock_lcd_init.return_value = None
    
    def stop_all_patch(self):
        patch.stopall()

    def test_with_correct_scenario(self):
        """
            Queue data is set and put with correct queue data and 
            ('cmd' key in queue data is 'NORMAL').
            Steps:
            1. Create queue data with size is more than 1.
            2. Put a payload to queue data.
            3. Initiate an lcd object from DisplayApp class
            4. Set queue data by invoking set_queue_data method
            5. Invoke _print_data method (since 'run' has infinite loop and 
               we only test non looping code)
        """
        self._help_mock_lcd_driver()
        q_data = mp.Queue(2)
        payload = {
            "cmd"     : "NORMAL",
            "payload" : ["Masukan no resi:", "0596"]
        }
        q_data.put(payload)
        lcd_t = DisplayApp()
        lcd_t.set_queue_data(q_data)
        lcd_t._print_data()

        self.mock_lcd_clear_lcd.assert_called_once()
        self.mock_lcd_write_text.assert_has_calls(
            [
               call (0, "Masukan no resi:"),
               call (1, "0596")
            ]            
        )
        self.stop_all_patch()

    def test_with_wrong_scenarion(self):
        """ cmd value is payload is not a string type,
         It should raise UnknownLcdOperation exception """
        with pytest.raises(AttributeError):
            self._help_mock_lcd_driver()
            q_data = mp.Queue(2)
            payload = {
                "cmd"     : DisplayMode.LLL,
                "payload" : ["Masukan no resi:", "0596"]
            }
            q_data.put(payload)
            lcd_t = DisplayApp()
            lcd_t.set_queue_data(q_data)
            lcd_t._print_data()


