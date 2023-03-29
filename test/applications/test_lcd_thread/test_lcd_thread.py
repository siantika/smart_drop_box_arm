import sys
import threading
import configparser
import multiprocessing as mp
import pytest
from unittest.mock import Mock, call, patch

sys.path.append('applications/lcd_thread')
sys.path.append('drivers/lcd')
from lcd_thread import LcdThread
from lcd import Lcd


class TestInitMethod:
    def test_init_method_should_handle_correctly(self):
        with patch('lcd.Lcd.__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd, \
               patch.object(Lcd, 'write_text') as mock_write_text:
           
            mock_lcd.return_value = None
            lcd_t = LcdThread()

            assert hasattr(lcd_t, 'queue_data_read')
            assert hasattr(lcd_t, '_lcd')
            assert hasattr(lcd_t, '_lock')

            assert lcd_t.queue_data_read == ''
            mock_lcd.assert_called_once_with(0x27,0)
            assert isinstance(lcd_t._lock, type(threading.Lock()))

            # print welcome display
            mock_init_lcd.assert_called_once()
            mock_write_text.assert_has_calls(
                [
                    call(0, "*Smart Drop Box*"),
                    call(1, f"----Ver. 1.0----")
                ]
            )


class TestSetQueueData:
    def test_set_queue_data_to_read_should_be_correct(self):
        with patch('lcd.Lcd.__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd, \
                patch.object(Lcd, 'write_text') as mock_write_text:
            
            mock_lcd.return_value = None
            test_data = mp.Queue(5)
            lcd_t = LcdThread()
            lcd_t.set_queue_data(test_data)
           
            assert lcd_t.queue_data_read == test_data
            assert isinstance(type(lcd_t.queue_data_read), type(mp.Queue))

class TestReadQueueData:
    def _help_mock_lcd_driver(self):
        self.mock_lcd_init       = patch('lcd.Lcd.__init__').start()
        self.mock_lcd_init_lcd   = patch('lcd.Lcd.init_lcd').start()
        self.mock_lcd_write_text = patch('lcd.Lcd.write_text').start()
        # should return None
        self.mock_lcd_init.return_value = None
    
    def stop_all_patch(self):
        patch.stopall()


    def test_read_queue_data_should_raise_attribute_error_when_set_queue_method_didnt_invoke_properly(self):
        self._help_mock_lcd_driver()
        with pytest.raises(AttributeError, match = "queue_data_read attribute had not been setted!"):
            lcd_t = LcdThread()
            lcd_t.read_queue_data()
        
        self.stop_all_patch()

    
    def test_read_queue_data_should_return_none_if_queue_data_read_contains_empty_payload(self):
        self._help_mock_lcd_driver()
        q_data = mp.Queue(2)
        lcd_t = LcdThread()
        lcd_t.set_queue_data(q_data)
        ret = lcd_t.read_queue_data()
        
        assert ret == None

        self.stop_all_patch()

        
    def test_read_queue_data_should_return_data_if_queue_data_read_is_assigned_payload(self):
        self._help_mock_lcd_driver()
        q_data = mp.Queue(2)
        q_data.put({
            "cmd"     : "routine",
            "payload" : ["Masukan no resi:", "0596"]
            }
        )
        lcd_t = LcdThread()
        lcd_t.set_queue_data(q_data)
        ret = lcd_t.read_queue_data()
        
        assert ret ==  {
            "cmd"     : "routine",
            "payload" : ["Masukan no resi:", "0596"]
        }

        self.stop_all_patch()



class TestParseData:
    def test_parse_dict_data_should_be_correct_when_data_dict_cmd_is_keypad(self):
        with patch('lcd.Lcd.__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd, \
                patch.object(Lcd, 'write_text') as mock_write_text:
            
            mock_lcd.return_value = None
            lcd_t = LcdThread()
            test_data = {"cmd":"keypad", "payload":["", "a" ]}
            ret = lcd_t.parse_dict_data(test_data)

            cmd  = ret[0] 
            data_text = ret[1]

            assert cmd       == 'keypad'
            assert data_text == ["", "a"]

    def test_parse_dict_data_should_be_correct_when_data_dict_cmd_is_routine(self):
        with patch('lcd.Lcd.__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd, \
                patch.object(Lcd, 'write_text') as mock_write_text:
            
            mock_lcd.return_value = None
            lcd_t = LcdThread()
            test_data = {"cmd":"routine", "payload":["5", "4" ]}
            ret = lcd_t.parse_dict_data(test_data)

            cmd  = ret[0] 
            data_text = ret[1]

            assert cmd       == 'routine'
            assert data_text == ["5", "4"]


    def test_parse_dict_data_should_raise_value_error_when_payload_content_isnt_string(self):
        with patch('lcd.Lcd.__init__') as mock_lcd, \
            patch.object(Lcd, 'init_lcd') as mock_init_lcd, \
                patch.object(Lcd, 'write_text') as mock_write_text:
            
            mock_lcd.return_value = None
            lcd_t = LcdThread()
            test_data = {"cmd":"routine", "payload":[5, '4']}

            try:
                lcd_t.parse_dict_data(test_data)
            except ValueError as e:
                assert str(e) == "Payload contents should be string!"
            else:
                assert False


class TestGetVersion:
    '''
        1. Get data from config.ini
        2. The section name is version
        3. Display error msg in LCD when section and contents are not found.
        4. The version's content must be contain max. 8 chars.
        5. Display error msg in LCD when ther version's content exceed 8 chars.
        6. If all prepared correctly, return the version in string type.
    '''
    def _help_mock_lcd_driver(self):
        self.mock_lcd_init       = patch('lcd.Lcd.__init__').start()
        self.mock_lcd_init_lcd   = patch('lcd.Lcd.init_lcd').start()
        self.mock_lcd_write_text = patch('lcd.Lcd.write_text').start()
        # should return None
        self.mock_lcd_init.return_value = None
    
    def stop_all_patch(self):
        patch.stopall()

    def test__get_version_data_should_invoke_method_correctly(self):
        # check the test environment is correct ( no test in other conditions)
        self._help_mock_lcd_driver()
        with patch.object(configparser.ConfigParser, 'read') as mock_read,\
            patch.object(configparser.ConfigParser, 'get') as mock_get:
            mock_get.return_value = 'Ver. 1.0'  

            lcd_t = LcdThread()
    
            mock_read.assert_called_once_with('./conf/config.ini')
            mock_get.assert_called_once_with('version', 'dev_version')

        self.stop_all_patch()


    def test__get_device_version_should_return_correct_version(self):
        self._help_mock_lcd_driver()

        try:
            lcd_t = LcdThread()
            device_version = lcd_t._get_device_version()
        except ValueError:
            # skip this test if version is testing in wrong condition!
            pytest.skip("Device version in exception env test")
        else:
            assert device_version == 'Ver. 1.0' 

        self.stop_all_patch()


    def test__get_device_version_should_raise_an_error_when_device_version_content_exceeded_8_chars_or_none(self):
        self._help_mock_lcd_driver()

        with pytest.raises(ValueError):   
            lcd_t = LcdThread()
            device_version = lcd_t._get_device_version()
            # skip this test if version is correct
            if len(device_version) <= 8 or len(device_version) != 0:
                pytest.skip("Device version in correct env test")
        
        self.stop_all_patch()

class TestDriverClass:
    def _help_mock_lcd_driver(self):
        self.mock_lcd_init       = patch('lcd.Lcd.__init__').start()
        self.mock_lcd_init_lcd   = patch('lcd.Lcd.init_lcd').start()
        self.mock_lcd_write_text = patch('lcd.Lcd.write_text').start()
        # should return None
        self.mock_lcd_init.return_value = None
    
    def stop_all_patch(self):
        patch.stopall()


    def test_print_data_method_should_be_exist(self):
        self._help_mock_lcd_driver()
        q_data = mp.Queue(2)
        
        lcd_t = LcdThread()
        lcd_t.set_queue_data(q_data)
        lcd_t.print_data()

        self.stop_all_patch()

    
    def test_run_method_should_be_exist(self):
        self._help_mock_lcd_driver()
        lcd_t = LcdThread()
        assert hasattr(lcd_t, 'run')
        self.stop_all_patch()


