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
import pytest 
import sys
import unittest
from unittest.mock import call, patch
sys.path.append('applications/network')
sys.path.append('drivers/database_connector')
from network_thread import Network
from database_connector import DatabaseConnector

TEST_LOCALHOST_ADDR = 'http://127.0.0.1/smart_drop_box/'

TEST_SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

class TestInitNetwork:
    def test_class_should_have_correct_attrib(self):
        net = Network()
        
        assert net.secret_key == TEST_SECRET_KEY_LOCAL
        assert isinstance (net.db_connection, DatabaseConnector)
        assert net.db_connection._base_url  == TEST_LOCALHOST_ADDR


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
            net = Network()
            ret = net._decode_json_to_dict(test_json_data)

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
        net = Network()

        ret = net._parse_dict(test_data)
        
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
        net = Network()

        ret = net._parse_dict(test_data)
        
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
        net = Network()

        ret = net._parse_dict(test_data)
        
        assert ret[0] == "DELETE"
        assert ret[1] == {}


class TestSetSecurityLocalServer:
    def test_set_security_should_be_invoked_correctly(self):
        net = Network()
        net._set_security(
            TEST_SECRET_KEY_LOCAL,
            'HS256',
            'Bearer',
        )

        assert net.db_connection._secret_key == TEST_SECRET_KEY_LOCAL
        assert net.db_connection._algo       == 'HS256'
        assert net.db_connection._token_type == 'Bearer'


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
        net = Network()

        ret = net.handle_commands(test_data)

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
        net = Network()
        net._set_security(
           secret_key=TEST_SECRET_KEY_LOCAL,
           algorithm='HS256',
           token_type='Bearer'
        )
        ret = net.handle_commands(test_data)
        http_response = ret[0]

        assert http_response == 200


class TestConfigParserSecretCorrect ():
    def test_read_config_parser_should_get_secret_key(self):
        net = Network()
        ret = net._read_config_file('server', 'secret_key')

        assert ret == TEST_SECRET_KEY_LOCAL


    def test_read_config_parser_should_get_server_address(self):
        net = Network()
        ret = net._read_config_file('server', 'address')

        assert ret == TEST_LOCALHOST_ADDR


class TestConfigParserSecretError (unittest.TestCase):
    '''
        check if section: secret is missing or typo!
    '''
    def test_config_parser_secret_should_raise_an_error_when_exception_no_section_occured(self):
        with pytest.raises(configparser.Error, match = "Section not found in configuration file"):
            net = Network()
            net._read_config_file( '', 'data_diri')
            

                


        




        


