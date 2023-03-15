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
import json
import queue
import sys
import unittest
from unittest.mock import call, patch
sys.path.append('applications/storage_thread')
sys.path.append('drivers/database_connector')
from storage_thread import StorageThread
from database_connector import DatabaseConnector

TEST_LOCALHOST_ADDR = 'http://127.0.0.1/smart_drop_box/'

TEST_SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

class TestInitStorageThread:
    def test_class_should_have_correct_attrib(self):
        storage_t = StorageThread()
        
        assert hasattr(storage_t, 'queue_from_thread_opt')
        assert hasattr(storage_t, 'queue_to_thread_opt')
        assert hasattr(storage_t, 'queue_from_thread_net')
        assert hasattr(storage_t, 'queue_to_thread_net')
        assert hasattr(storage_t, 'db')
        assert hasattr(storage_t, 'secret_key_local')

        assert storage_t.queue_from_thread_opt == ""
        assert storage_t.queue_to_thread_opt   == ""
        assert storage_t.queue_from_thread_net == ""
        assert storage_t.queue_to_thread_net   == ""
        assert storage_t.secret_key_local      == ""

        assert isinstance (storage_t.db, DatabaseConnector)
        assert storage_t.db._base_url == TEST_LOCALHOST_ADDR


    def test_set_queue_should_be_correct(self):
        q_to_thd_opt = queue.Queue()
        q_from_thd_opt = queue.Queue()
        q_from_thd_net = queue.Queue()
        q_to_thd_net   = queue.Queue()
                  
        storage_t = StorageThread()

        storage_t.set_queue(
            q_from_thd_opt,
            q_to_thd_opt,
            q_from_thd_net,
            q_to_thd_net
        )

        assert isinstance(storage_t.queue_from_thread_opt, queue.Queue)
        assert isinstance(storage_t.queue_to_thread_opt, queue.Queue)
        assert isinstance(storage_t.queue_from_thread_net, queue.Queue)
        assert isinstance(storage_t.queue_to_thread_net, queue.Queue)


class TestDecodeJsonMethod:
    def test_decode_json_to_dict_should_be_correct(self):
        test_data = \
            {
            "name" : "arduino uno",
            "no_resi" : "0023",
            }
        
        test_json_data = json.dumps(test_data)
        with patch('json.loads') as mock_loads:
            mock_loads.return_value = test_data
            storage_t = StorageThread()

            ret = storage_t.decode_json_to_dict(test_json_data)

            mock_loads.assert_called_once_with(test_json_data)
            assert ret == test_data
            assert isinstance(ret, dict)



class TestParseDataMethod:
    def test_data_parse_dict_should_parsed_data_and_return_correctly(self):
        test_data = \
        {   "method"  : "POST",
            "name"    : "LCD",
            "no_resi" : "0023"
        }
        storage_t = StorageThread()

        ret = storage_t.parse_dict(test_data)
        
        assert ret[0] == "POST"
        assert ret[1] ==  \
             {  "name"    : "LCD",
                "no_resi" : "0023"
             }
        
    def test_data_parse_dict_should_parsed_data_and_return_when_dict_data_increasing_correctly(self):
        test_data = \
        {   "method"  : "UPDATE",
            "id"      : "2",
            "name"    : "LCD",
            "no_resi" : "0023",
            "date_created" : "29-02-2023"
        }
        storage_t = StorageThread()

        ret = storage_t.parse_dict(test_data)
        
        assert ret[0] == "UPDATE"
        assert ret[1] ==  \
             {             
                "id"      : "2",
                "name"    : "LCD",
                "no_resi" : "0023",
                "date_created" : "29-02-2023"
             }
    

    def test_data_parse_dict_should_parsed_data_and_return_correctly_when_no_dict_data_decreas(self):
        test_data = \
        {   "method"  : "DELETE",
        }
        storage_t = StorageThread()

        ret = storage_t.parse_dict(test_data)
        
        assert ret[0] == "DELETE"
        assert ret[1] == {}



class TestSetSecurityLocalServer:
    def test_set_security_should_be_invoked_correctly(self):
        storage_t = StorageThread()
        storage_t.set_security(
            TEST_SECRET_KEY_LOCAL,
            'HS256',
            'Bearer',
        )

        assert storage_t.db._secret_key == TEST_SECRET_KEY_LOCAL
        assert storage_t.db._algo       == 'HS256'
        assert storage_t.db._token_type == 'Bearer'


class TestRequestMethod:
    def test_request_method_should_invoke_correctly_when_method_is_get(self):
        '''
            get data from parsed dict,
            excute base on methods,
            return status, data if GET method
        '''
        test_data = {"method" : "GET",
                      "id" : "50"
                      }
        storage_t = StorageThread()

        ret = storage_t.handle_commands(test_data)

        http_response = ret[0]
        response_text = ret[1]

        assert http_response == 200
        assert response_text == {"id":50,
                                 "name":"Arduino Mega",
                                 "no_resi":"0023",
                                 "date_time":"2023-03-04 22:59:41"
                                 }
        
    def test_request_method_should_invoke_correctly_when_method_is_post(self):
        test_data = {"method" : "POST",
                      "name" : "breadboard",
                      "no_resi" : "6005"
                      }
        storage_t = StorageThread()
        storage_t.set_security(
           secret_key=TEST_SECRET_KEY_LOCAL,
           algorithm='HS256',
           token_type='Bearer'
        )

        ret = storage_t.handle_commands(test_data)
        http_response = ret[0]

        assert http_response == 200


class TestSendQueueData:
    def test_queue_send_data_should_process_correctly(self):
        q1 = queue.Queue(2)
        q2 = queue.Queue(2)
        q3 = queue.Queue(2)

        test_data = {
            "method" : "get",
            "name"   : "obeng",
            "no_resi": "5523"
        }

        with patch('queue.Queue.put') as mock_put:
            str_t = StorageThread()
            str_t.set_queue(q1, q2, q3)
            str_t.send_queue_data(test_data, q2)
            mock_put.assert_called_once_with(test_data, block=False)



class TestReadQueueData:
    def test_read_queue_data_should_be_invoked_correctly(self):
        with patch('queue.Queue.get') as mock_get:
            mock_get.return_value = {"name":"solder"}
            str_t = StorageThread()
            q = queue.Queue(5)
            q.put({"name":"solder"})

            _ret_val = str_t.read_queue_data(q)

            mock_get.assert_called_once()
            assert _ret_val == {"name":"solder"}


    def test_read_queue_data_should_return_empty_if_the_queue_is_empty(self):
        str_t = StorageThread()
        q = queue.Queue(1)
        _ret_val = str_t.read_queue_data(q)

        assert _ret_val == 'empty'


class TestRunMethod:
    def test_read__queue_data_from_server_should_handled_correctly_when_called_with_post_metho(self):
        q_to_opt      = queue.Queue(5)
        q_from_opt    = queue.Queue(5)
        q_from_server = queue.Queue(5)
        q_to_server   = queue.Queue(5)
        
        q_from_server.put(
            {
                "method"  : "post",
                "name"    : "SHT11",
                "no_resi" : "0502"
            }
        )
        str_t = StorageThread()
        str_t.set_queue( 
            queue_from_thread_opt =  q_from_opt, 
            queue_to_thread_opt   =  q_to_opt,
            queue_from_thread_net = q_from_server, 
            queue_to_thread_net   = q_to_server)

        str_t.run()



class TestConvertToDict:
    '''
        from tuple to dict, 2 items only
    '''
    def test_convert_to_dict_method_should_handle_correctly(self):
        str_t =StorageThread()

        test_data = (404, 'Data not found' )

        ret = str_t._convert_to_dict(test_data)

        assert ret == {
            'status_code' : 404,
            'response'    : 'Data not found'
        }



class TestConfigParserSecretCorrect (unittest.TestCase):
    def test_config_parser_secret_should_get_correct_secret(self):
        with patch.object(configparser.ConfigParser, 'read') as mock_read, \
            patch.object(configparser.ConfigParser, 'get') as mock_get:
            mock_read.return_value = True
            mock_get.return_value = 'ini_s3cr37'

            str_t = StorageThread()
            ret = str_t._get_secret()

            mock_read.assert_called_once_with('./conf/config.ini')
            mock_get.assert_called_once_with('secret', 'local_server_secret_key')

            assert ret == 'ini_s3cr37'


class TestConfigParserSecretError (unittest.TestCase):
    '''
        check if section: secret is missing or typo!
    '''
    def test_config_parser_secret_should_raise_an_error_when_exception_no_section_occured(self):
        with self.assertRaises(configparser.NoSectionError, msg="Secret section not found!"):
            str_t = StorageThread()
            str_t._get_secret()
            

                


        




        


