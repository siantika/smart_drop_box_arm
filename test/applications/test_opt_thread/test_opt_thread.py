import queue
import sys
import threading
import pytest
import multiprocessing as mp
from unittest.mock import patch
sys.path.append('applications/operation_thread')
sys.path.append('applications/network_thread')
from operation_thread import ThreadOperation
from network_thread import NetworkThread


class TestThreadOperation:
    def test_init_method_should_be_correct(self):
        opt_t = ThreadOperation()
        assert opt_t.queue_data_to_lcd == ''
        assert opt_t.st_msg_has_not_displayed == True
        assert isinstance(opt_t.lock, type(threading.Lock())) 


    def test_set_queues_data_network_thread_should_be_correct(self):
        q_data_read = queue.Queue(2)
        q_data_send = queue.Queue(2)
        opt_t = ThreadOperation()
        opt_t.set_queues_network_thread(
            q_data_read, q_data_send
        )
        assert opt_t.queue_data_from_network == q_data_read
        assert opt_t.queue_data_to_network  == q_data_send


    def test_set_queue_data_to_lcd_thread_should_be_correct(self):
        q_data_send = queue.Queue(2)
        opt_t = ThreadOperation()
        opt_t.set_queue_to_lcd_thread(
            q_data_send
        )
        assert opt_t.queue_data_to_lcd  == q_data_send


class TestDataConvertion:      

    def test_create_data_object_should_be_able_create_lcd_data_object_correctly(self):
        thread_name = 'lcd'
        method = "keypad"
        method2 = "routine"
        opt_t = ThreadOperation()

        ret_val = opt_t._create_data_object(thread_name, method, first_line = "Masukan resi:", second_line = "0")

        assert ret_val == {
            "cmd" : "keypad",
            "payload": ["Masukan resi:", "0"]
        }

        ret_val2 = opt_t._create_data_object(thread_name, method2, first_line = "itms arrived : 5", second_line = "itms stored : 2")
        assert ret_val2 == {
            "cmd": "routine",
            "payload" : ["itms arrived : 5", "itms stored : 2"]
        }

 
    def test__create_data_object_should_return_correctly_when_is_data_object_is_true(self):
        app_name = 'network'
        method   = 'POST'
        
        opt_t = ThreadOperation()
        
        ret_val = opt_t._create_payload(app_name, method, True, data_object = {'no_resi' : '0000', 'name' : 'arduino', 'date_ordered' : "2023-03-23 09:53:39"})

        assert ret_val == {
            'method' : 'POST',
            'payload' : {'no_resi' : '0000', 'name' : 'arduino', 'date_ordered' : "2023-03-23 09:53:39"}
        }



    def test_send_queue_data_should_handle_correctly(self):
        test_data = {
            'cmd' : 'routine',
            'payload' : ["halo", "sian"]
        }
        q_data_to_send_lcd = queue.Queue(2)
        opt_t = ThreadOperation()
        opt_t.set_queue_to_lcd_thread(q_data_to_send_lcd)
        opt_t._send_data_queue(opt_t.queue_data_to_lcd, test_data)
        data_read = opt_t.queue_data_to_lcd.get()
        assert data_read == test_data

    
    def test_send_queue_data_should_return_full_if_queue_is_full(self):
        test_data = {
            'cmd' : 'routine',
            'payload' : ["halo", "sian"]
        }
        q_data_to_send_lcd = queue.Queue(1)
        opt_t = ThreadOperation()
        opt_t.set_queue_to_lcd_thread(q_data_to_send_lcd)
        data = opt_t._send_data_queue(opt_t.queue_data_to_lcd, test_data)
        data = opt_t._send_data_queue(opt_t.queue_data_to_lcd, test_data)
        assert data == 'full'


class TestNetworkMethod:
    def test_network_should_initialize_correctly(self):
        opt_t = ThreadOperation()
        assert isinstance(opt_t.network, NetworkThread)


class TestPrivateMethods:

    def test_make_initial_should_be_correct(self):
        test_data = [
            {
                'no_resi' : '0000',
                'name'    : 'Arduino',
                'date_ordered' : '2023-03-23 09:53:39'
            },
            {
                'no_resi' : '0020',
                'name'    : 'Esp32',
                'date_ordered' : '2023-03-23 09:53:39'
            }
        ]
        
        opt_t = ThreadOperation()

        ret_val = opt_t._make_initial_data(test_data)

        assert ret_val ==  {
            '0000' : 0,
            '0020' : 1            
        }


class TestConfig:
    def test_get_data_from_config_file_should_correct(self):
        with patch.object(ThreadOperation, '__init__') as mock_init:   
            mock_init.return_value = None 
            opt_t = ThreadOperation()
            data = opt_t.get_data_from_config("pass", "universal_password")
            assert data == "CAD*"

    def test_check_universal_password_should_raise_error_when_called_with_wrong_value(self):
        with patch.object(ThreadOperation, '__init__') as mock_init, \
            pytest.raises(ValueError), patch.object(ThreadOperation, '_send_data_queue') as mock_send_queue:   
            mock_init.return_value = None 
            opt_t = ThreadOperation()
            opt_t.check_universal_password("asdsaasxcaer")

    
    def test_check_universal_passwrod_should_return_correct_value_when_called_with_correct_value(self):
        with patch.object(ThreadOperation, '__init__') as mock_init: 
            mock_init.return_value = None 
            opt_t = ThreadOperation()
            opt_t.check_universal_password("ABC*")