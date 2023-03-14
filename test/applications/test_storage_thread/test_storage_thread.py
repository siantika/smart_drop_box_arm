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
import json
import queue
import sys
from unittest.mock import patch
sys.path.append('applications/storage_thread')
sys.path.append('drivers/database_connector')
from storage_thread import StorageThread
from database_connector import DatabaseConnector

TEST_LOCALHOST_ADDR = '127.0.0.1'

TEST_SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

class TestInitStorageThread:
    def test_class_should_have_correct_attrib(self):
        storage_t = StorageThread()
        
        assert hasattr(storage_t, 'queue_from_thread_opt')
        assert hasattr(storage_t, 'queue_to_thread_opt')
        assert hasattr(storage_t, 'queue_from_thread_net')
        assert hasattr(storage_t, 'db')

        assert storage_t.queue_from_thread_opt == ""
        assert storage_t.queue_to_thread_opt   == ""
        assert storage_t.queue_from_thread_net  == ""

        assert isinstance (storage_t.db, DatabaseConnector)
        assert storage_t.db._url == TEST_LOCALHOST_ADDR


    def test_set_queue_should_be_correct(self):
                # queue_from_thread_opt:queue.Queue,
                # queue_to_thread_opt:queue.Queue,
                # queue_from_webserver:queue.Queue
        q_to_thd_opt = queue.Queue()
        q_from_thd_opt = queue.Queue()
        q_from_thd_net = queue.Queue()
                  
        storage_t = StorageThread()

        storage_t.set_queue(
            q_from_thd_opt,
            q_to_thd_opt,
            q_from_thd_net
        )

        assert isinstance(storage_t.queue_from_thread_opt, queue.Queue)
        assert isinstance(storage_t.queue_to_thread_opt, queue.Queue)
        assert isinstance(storage_t.queue_from_thread_net, queue.Queue)


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
            {}
        )

        assert storage_t.db._secret_key == TEST_SECRET_KEY_LOCAL
        assert storage_t.db._algo       == 'HS256'
        assert storage_t.db._token_type == 'Bearer'


    # def test_set_security_should_invoke_encode_method_from_db_connector_lib(self):
    #     test_db_con = DatabaseConnector('127.0.0.1')

    #     with patch.object(test_db_con, 'encode') as mock_encode:
    #         storage_t =StorageThread()
    #         storage_t.set_security(
    #         TEST_SECRET_KEY_LOCAL,
    #         'HS256',
    #         'Bearer',
    #         {}
    #            )
    #         mock_encode.assert_called_once_with({})


class TestRequestMethod:
    def test_request_method_should_invoke_correctly_when_method_is_get(self):
        '''
            get data from parsed dict,
            excute base on methods,
            return status, data if GET method
        '''
        test_data = {"method" : "GET",
                      "id" : "20"
                      }
        storage_t = StorageThread()

        ret = storage_t.send_request(test_data)

        http_response = ret[0]
        response_text = ret[1]

        assert http_response == 200
        assert response_text == {
            "id":20,
            "name":"bola",
            "no_resi":"7777",
            "date_time":"2023-03-04 20:53:32"
            }
        
    def test_request_method_should_invoke_correctly_when_method_is_post(self):
        test_data = {"method" : "POST",
                      "name" : "breadboard",
                      "no_resi" : "6005"
                      }
        
        storage_t = StorageThread()

        ret = storage_t.send_request(test_data)

        http_response = ret[0]

        assert http_response == 200


    # def test_send_request_should_execute_correctly_when_method_get(self):
    #     test_data = ("GET", "20")
    #     storage_t = StorageThread()

    #     storage_t.send_request(test_data)



      




        


