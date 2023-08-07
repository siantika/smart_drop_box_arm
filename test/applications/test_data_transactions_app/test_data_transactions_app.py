'''
    methods:
        1. Parse data from dict:
            + method [post, update, delete]
            + payload data [name, no_resi, date_created]
        2. Request data to local server:
            return status_data and data in JSON format if(GET method).
        3. Decode json to dict obj
            return dict

'''
import configparser
import os
import pytest 
import sys
import multiprocessing as mp
from unittest.mock import patch

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'src/applications/data_transactions_app'))
sys.path.append(os.path.join(parent_dir, 'src/drivers/data_access'))
sys.path.append(os.path.join(parent_dir, 'src/utils'))
full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')

from data_transactions_app import *
from data_access import HttpDataAccess

# Constants for tests environment
TEST_LOCALHOST_ADDR = 'http://127.0.0.1/smart_drop_box/'
TEST_SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'


class TestEndpointProcessor:
    def help_mock_data_access(self):
        patch.stopall()
        self._mock_get_method = patch.object(HttpDataAccess, 
                                              'get').start()
        self._mock_post_method = patch.object(HttpDataAccess, 
                                              'post').start()
        self._mock_update_method = patch.object(HttpDataAccess, 
                                              'update').start()
        self._mock_delete_method = patch.object(HttpDataAccess, 
                                              'delete').start()
        
    test_endpoint_metadata = {
        'get':['get.php'],
        'post':['success_item.php', 'post.php'],
        'update':['update.php'],
        'delete': ['delete.php'],
    }

    def test_with_correct_get_method_and_payload(self):
        test_data = {
            "endpoint"  : "get.php",
            "data" :{"no_resi" : "0023"},
            "http_header" : {"content-type" : "application/json"}
        }
        self.help_mock_data_access()
        data_access = HttpDataAccess(TEST_LOCALHOST_ADDR)
        end_processor = EndpointProcessor(self.test_endpoint_metadata,
                                          data_access)
        end_processor.process(test_data)
        self._mock_get_method.assert_called_once_with(
            param = {"no_resi" : "0023"},
            endpoint = "get.php",
            http_header = {"content-type" : "application/json"},
            timeout = 10,
        )

    def test_with_correct_post_multipart(self):
        test_data = {
            "endpoint"  : "success_item.php",
            "data" :{"no_resi" : "0023", "item":"sikat gigi", "file":"image.jpg"},
            "http_header" : {"content-type" : "application/json"}
        }
        self.help_mock_data_access()
        data_access = HttpDataAccess(TEST_LOCALHOST_ADDR)
        end_processor = EndpointProcessor(self.test_endpoint_metadata,
                                          data_access)
        end_processor.process(test_data)
        self._mock_post_method.assert_called_once_with(
            param = {"no_resi" : "0023", "item":"sikat gigi", 
                     "file":"image.jpg"},
            endpoint = "success_item.php",
            http_header = {"content-type" : "application/json"},
            timeout = 10,
        )
        
    def test_with_correct_post_method_and_payload(self):
        test_data = {
            "endpoint"  : "post.php",
            "data" :{"no_resi" : "0023", "item":"sikat gigi"},
            "http_header" : {"content-type" : "application/json"}
        }
        self.help_mock_data_access()
        data_access = HttpDataAccess(TEST_LOCALHOST_ADDR)
        end_processor = EndpointProcessor(self.test_endpoint_metadata,
                                          data_access)
        end_processor.process(test_data)
        self._mock_post_method.assert_called_once_with(
            param = {"no_resi" : "0023", "item":"sikat gigi"},
            endpoint = "post.php",
            http_header = {"content-type" : "application/json"},
            timeout = 10,
        )
        
    def test_with_correct_update_method_and_payload(self):
        test_data = {
            "endpoint"  : "update.php",
            "data" :{"old_resi" : "0023", 
                     "new_resi" : "1121",
                     "name":"batok kelapa"},
            "http_header" : {"content-type" : "application/json"}
        }
        self.help_mock_data_access()
        data_access = HttpDataAccess(TEST_LOCALHOST_ADDR)
        end_processor = EndpointProcessor(self.test_endpoint_metadata,
                                          data_access)
        end_processor.process(test_data)
        self._mock_update_method.assert_called_once_with(
            param = {"old_resi" : "0023", 
                     "new_resi" : "1121",
                     "name":"batok kelapa"},
            endpoint = "update.php",
            http_header = {"content-type" : "application/json"},
            timeout = 10,
        )
        
    def test_with_correct_delete_method_and_payload(self):
        test_data = {
            "endpoint"  : "delete.php",
            "data" :{"no_resi" : "0023"},
            "http_header" : {"content-type" : "application/json"}
        }
        self.help_mock_data_access()
        data_access = HttpDataAccess(TEST_LOCALHOST_ADDR)
        end_processor = EndpointProcessor(self.test_endpoint_metadata,
                                          data_access)
        end_processor.process(test_data)
        self._mock_delete_method.assert_called_once_with(
            param = {"no_resi" : "0023"},
            endpoint = "delete.php",
            http_header = {"content-type" : "application/json"},
            timeout = 10,
        )

    def test_with_unknown_method(self):
        with pytest.raises(ValueError, match="Endpoint not found or not registered!"):
            test_data = {
                "endpoint"  : "registrasi_baru.php",
                "data" :{"id" : "id5656", "pass":"pastibisa3323"},
                "http_header" : {"content-type" : "application/json"}
            }
            self.help_mock_data_access()
            data_access = HttpDataAccess(TEST_LOCALHOST_ADDR)
            end_processor = EndpointProcessor(self.test_endpoint_metadata,
                                            data_access)
            end_processor.process(test_data)
            patch.stopall()


""" Test utility functions """
class TestConfigParserSecretError:
    '''
        Test functionalities of config parser
    '''
    def test_with_unknown_section_param(self):
        with pytest.raises(configparser.Error):
            read_config_file(full_path_config_file,'', 'data_diri')

    def test_with_correct_params(self):
        """ Please check """
        assert "https://dropbox.smart-monitoring.my.id/" == read_config_file(full_path_config_file,
                                                                             'server','address')
    
    def test_with_wrong_config_path_param(self):
        with pytest.raises(configparser.Error):
            read_config_file("d:downloads", 'server', 'address')


""" Integration tests """
class TestSendRequests:
    """ 
        Test send requests with correct payload and wrong payload.
    """
    def help_mock_data_access(self):
        """ Helps mock the responses from server"""
        patch.stopall()
        self._mock_get_method = patch.object(HttpDataAccess, 
                                              'get').start()
        self._mock_post_method = patch.object(HttpDataAccess, 
                                              'post').start()
        self._mock_update_method = patch.object(HttpDataAccess, 
                                              'update').start()
        self._mock_delete_method = patch.object(HttpDataAccess, 
                                              'delete').start()
        # Return mocks responses
        self._mock_update_method.return_value = (201, "Success updated data")
        self._mock_post_method.return_value = (204, "Posted successfully")

    def test_with_correct_payload(self,caplog):
        """ 
            Should emptying the queue while queue inserted by 1 data,
            should log the response,
            and should send correct data to data access object
        """
        self.help_mock_data_access()
        test_queue_data = mp.Queue(2)
        test_payload = {
                "endpoint":"post.php",
                "data" :{"no_resi" : "0023", "item":"sikat gigi"},
                "http_header" : {"content-type" : "application/json"}
                }
        test_queue_data.put(test_payload)

        send_app = HttpSendDataApp()
        send_app.set_queue_data(test_queue_data)
        send_app._send_request_app()
        # Queue data should be empty due to putted by send_app 
        assert test_queue_data.empty() == True
        # Should log the response
        assert caplog.messages[0] =="Response dari request : Posted successfully"
        # Should called with correct data for data access
        self._mock_post_method(
            endpoint = 'post.php',
            payload  = {'no_resi' : '0023', 'item':'sikat gigi'},
            http_header = {'content-type' : 'application/json'}
        ) 

    def test_with_uncorrect_payload_endpoint(self):
        """ 
            Should raise a Value Error: endpoint not found ...
        """
        with pytest.raises(ValueError):
            self.help_mock_data_access()
            test_queue_data = mp.Queue(5)
            test_payload = {
                    "endpoint":"wrong_data.php",
                    "data" :{"no_resi" : "0023", "item":"sikat gigi"},
                    "http_header" : {"content-type" : "application/json"}
                    }
            test_queue_data.put(test_payload)

            send_app = HttpSendDataApp()
            send_app.set_queue_data(test_queue_data)
            send_app._send_request_app()
            patch.stopall()


class TestGetRequestsRoutine:
    """ Test get requests from server """
    def _help_mock_get_requests(self):
        self._mock_get_requests = patch.object(HttpDataAccess, 'get').start()

    def test_with_exists_get_response_data(self):
        """ Get requests should be called once,
            Return the response text/content only """
        self._help_mock_get_requests()
        self._mock_get_requests.return_value = ( 200, [{
            'no_resi' : '0789',
            'item' : 'tamiya',
            'date_ordered' : '27/02/2023'
            }, 
            {
            'no_resi' : '5565',
            'item' : 'setrika',
            'date_ordered' : '25/02/2024',
            }
            ])
        test_queue = mp.Queue(2)
        get_requests_app = HttpGetResiDataRoutineApp()
        get_requests_app.set_queue_data(test_queue)
        get_requests_app._get_request_routine()
        # Tests
        self._mock_get_requests.assert_called_once()
        assert test_queue.get() == {'0789' : {
            'no_resi' : '0789',
            'item' : 'tamiya',
            'date_ordered' : '27/02/2023'
        },
            '5565' : {
                'no_resi' : '5565',
                'item' : 'setrika',
                'date_ordered' : '25/02/2024',
            }
        }
        patch.stopall()

    def test_with_no_get_response_data(self):
        """ No get method invoked and queue is empty
         (no new data)"""
        self._help_mock_get_requests()
        test_queue = mp.Queue(2)
        get_requests_app = HttpGetResiDataRoutineApp()
        get_requests_app.set_queue_data(test_queue)
        get_requests_app._get_request_routine()
        # Tests
        not self._mock_get_requests.assert_called_once()
        assert test_queue.empty()
        patch.stopall()

    def test_with_twice_same_response_data(self):
        """ Should send the first data, ignore the second data """
        self._help_mock_get_requests()
        self._mock_get_requests.return_value = ( 200, [{
            'no_resi' : '0789',
            'item' : 'tamiya',
            'date_ordered' : '27/02/2023'
            }, 
            {
            'no_resi' : '5565',
            'item' : 'setrika',
            'date_ordered' : '25/02/2024',
            }
            ])
        test_queue = mp.Queue(4)
        get_requests_app = HttpGetResiDataRoutineApp()
        get_requests_app.set_queue_data(test_queue)
        # invoke it twice with the same data
        get_requests_app._get_request_routine()
        get_requests_app._get_request_routine()
        assert test_queue.get() == {'0789' : {
            'no_resi' : '0789',
            'item' : 'tamiya',
            'date_ordered' : '27/02/2023'
        },
            '5565' : {
                'no_resi' : '5565',
                'item' : 'setrika',
                'date_ordered' : '25/02/2024',
            }
        }
        patch.stopall()
# EOF
