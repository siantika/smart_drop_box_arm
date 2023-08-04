'''
 Test cases for data access driver (unit and integration tests).

'''

from unittest.mock import patch
import requests
import sys
import pytest
import os 
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'src/drivers/data_access'))
from data_access import *


TEST_URL        = 'http://localhost.com/smart_drop_box/'
TEST_GET_URL    = 'http://localhost.com/smart_drop_box/get.php'
TEST_URL_POST   = 'http://localhost.com/smart_drop_box/post.php'
TEST_UPDATE_URL = 'http://localhost.com/smart_drop_box/update.php'
TEST_DELETE_URL = 'http://localhost.com/smart_drop_box/delete.php'

SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'
TEST_GENERATED_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
TEST_ENDPOINT = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php',
                       'post-multipart' : 'success_items.php'}

class HelpMockMethod:
    def help_mock_api_response(self, status_code:int = None, payload:any= None, is_json=False):
        self.mock_request_get = patch('requests.request').start()
        self.mock_request_get.return_value.status_code = status_code
        if is_json is True:
            payload = json.dumps(payload)
        self.mock_request_get.return_value.text = payload
        

class TestHttpRequestData:
    """ Tests http requests resposes """
    def test_basic_request(self):
        data = HttpRequestData(endpoint_url="https://api.example.com", method="GET", header={"Content-Type": "application/json"})
        assert  data.endpoint_url == "https://api.example.com"
        assert data.method == "GET"
        assert data.header == {"Content-Type": "application/json"}
        assert not data.data
        assert not data.param
        assert not data.file
        assert not data.time_out

    def test_with_data_and_params(self):
        data = {"key1": "value1", "key2": "value2"}
        params = {"param1": "param_value"}
        request = HttpRequestData(
            endpoint_url="https://api.example.com",
            method="POST",
            header={"Authorization": "Bearer <your_access_token>"},
            data=data,
            param=params,
        )
        assert request.method == "POST"
        assert request.data == data
        assert request.param == params

    def test_with_file(self):
        # Mock an IO stream for the file
        file_content = b"file content"
        file_stream = IO()
        file_stream.write(file_content)
        file_stream.seek(0)

        request = HttpRequestData(
            endpoint_url="https://api.example.com/upload",
            method="POST",
            header={"Content-Type": "multipart/form-data"},
            file={"file.txt": file_stream},
        )
        assert request.method == "POST"
        assert request.file == {"file.txt": file_stream}


class TestHttpDataAccessInit:
    """ Test the constructor of Http data class """
    def test_should_inherit_from_data_access_interface(self):
        assert issubclass(HttpDataAccess, DataAccess)

    def test_with_correct_url_and_endpoint(self):
        data = HttpDataAccess(
            TEST_URL,
        )
        assert not data._token

    def test_with_no_backlash_in_the_end_of_url(self):
        with pytest.raises(ValueError):
            data = HttpDataAccess(
                'https://api-example.org',
                TEST_ENDPOINT
            )

    def test_with_token(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        assert data._token == TEST_GENERATED_TOKEN


class TestDataAccessPrivateMethod:
    """ Tests the private methods of data acces class"""
    def test_with_exist_endpoint(self):
        """ full url get.php-endpoint should correct """
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        assert data._make_full_url_endpoint('get.php') == str(data._base_url \
                                                          + TEST_ENDPOINT['get'])
                    

class TestHttpDataAccessGetMethod(HelpMockMethod):
    """ Tests the get method in http data access class in posible scenarios """
    def test_with_invalid_payload_type(self):
        self.help_mock_api_response()
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Param argument should be dictionary type !"):
            http_header = {'content-type' : 'application/json'}
            data.get([{'no_resi' : '5563'}], 'get', http_header)
            
    def test_with_invalid_header_type(self):
        self.help_mock_api_response()
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Http header argument should be dictionary type !"):
            http_header = [{'content-type' : 'application/json'}]
            data.get({'no_resi' : '5563'}, 'get', http_header)            

    def test_with_success_return_data(self):
        test_payload = {
            'no_resi' : '0230',
            'item' : 'sapu lidi',
        }
        self.help_mock_api_response(200, test_payload, True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({'no_resi' : '0230 '}, 'get', http_header)
        assert data_retrieved[0] == 200
        assert data_retrieved[1] == test_payload

    def test_with_empty_param(self):
        api_response = [
            {
                'no_resi' : '0256',
                'item' : 'Sapu lidi'
            },
            {
                'no_resi' : '3693',
                'item' : 'Porselin'
            },
            {
                'no_resi' : '9696',
                'item' : 'Sendok'
            }
        ]
        self.help_mock_api_response(200, api_response, True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({}, 'get', http_header)
        assert data_retrieved[0] == 200
        assert data_retrieved[1] == api_response

    def test_with_not_found_data(self):
        self.help_mock_api_response(404, 'data not found', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({'no_resi' : '0230 '}, 'get', http_header)
        assert data_retrieved[0] == 404
        assert data_retrieved[1] == "The requested resource could not be found."

    def test_with_unknown_status_code_response(self):
        self.help_mock_api_response(999, 'unknown problem!', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({'no_resi' : '0230 '}, 'get', http_header)
        # Not in STATUS_MESSAGES Response handler class variable
        assert data_retrieved[0] is not data._http_request._response_handler.STATUS_MESSAGES.keys()
        assert data_retrieved[1] == "999"

    def test_with_data_does_not_return_json_format(self):
        self.help_mock_api_response(500, 'Internal server error')
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({'no_resi' : '0230 '}, 'get', http_header)
        assert data_retrieved[0]  == 500
        assert data_retrieved[1] == "Internal server error"

    def test_with_success_request_but_no_return_data(self):
        self.help_mock_api_response(204, None, True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({'no_resi' : '0230 '}, 'get.php', http_header)
        assert data_retrieved[0]  == 204
        assert data_retrieved[1] == "The request was successful but there is no content to return."

    def test_with_no_endpoint(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(TypeError):
            http_header = {'content-type' : 'application/json'}
            data.get({'no_resi' : '0230 '}, http_header)
    

    def test_with_no_token(self, caplog):
        """ Should log a warning "not authorized !"""
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.get({'no_resi' : '0230 '}, 'get.php', 
                                  http_header)
        
        log_messages = caplog.messages[0]
        assert log_messages == "Your request is not authorized!"
            

class TestHttpDataAccessPostMethod(HelpMockMethod):

    def test_with_invalid_payload_type(self):
        self.help_mock_api_response()
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Payload argument should be dictionary type !"):
            http_header = {'content-type' : 'application/json'}
            data.post([{'no_resi' : '5563', 'item' : 'iphone20'}],'post', http_header)
            
    def test_with_invalid_header_type(self):
        self.help_mock_api_response()
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Http header argument should be dictionary type !"):
            http_header = [{'content-type' : 'application/json'}]
            data.post({'no_resi' : '5563', 'item' : 'Iphone 20'}, 'post', http_header)
            
    def test_with_success_request(self):
        test_payload = {
            'no_resi' : '0230',
            'item' : 'Buku tulis Sidu',
        }
        self.help_mock_api_response(201, test_payload, True )
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.post({'no_resi' : '0230', 'item':'Buku tulis Sidu'}, 'post', http_header)
        assert data_retrieved[0]  == 201
        assert data_retrieved[1] == test_payload        

    def test_with_data_does_not_return_json_format(self):
        self.help_mock_api_response(500, 'Internal server error')
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.post({'no_resi' : '0230', 'item':'Buku tulis Sidu'}, 'post', http_header)
        assert data_retrieved[0]  == 500
        assert data_retrieved[1] == "Internal server error"

    def test_with_invalid_request(self):
        self.help_mock_api_response(400, 'Invalid request', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.post({'no_resasdasi' : '0230', 'iteasm':'Bdduku tulis Sidu'}, 'post', http_header)
        assert data_retrieved[0]  == 400
        assert data_retrieved[1] == "The request was invalid or cannot be otherwise served."

    def test_with_unknown_status_code_response(self):
        self.help_mock_api_response(582, 'unknown problem!', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.post({'no_resi' : '0230', 'item':'Buku tulis Sidu'}, 'post', http_header)
        # Not in STATUS_MESSAGES Response handler class variable
        assert data_retrieved[0] is not data._http_request._response_handler.STATUS_MESSAGES.keys()
        assert data_retrieved[1] == "582"

    def test_with_correct_file(self):
        # Mock an IO stream for the file
        file_content = b"file content"
        file_stream = IO()
        file_stream.write(file_content)
        file_stream.seek(0)
        photo_payload = {'photo' : file_stream}
        api_response = {
            'no_resi' : '5563',
            'item' : 'Casing android phone',
            'file' : 'https://smart_drop.com/upload/images/photo-2023-03-22.jpg'
        }
        self.help_mock_api_response(201, api_response, True )
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'multipart/form'}
        data_retrieved = data.post({
            'no_resi' : '5563',
            'item' : 'Casing android phone',
        }, 'post-multipart', http_header, photo_payload)
        assert data_retrieved[0]  == 201
        assert data_retrieved[1] == api_response 

    @patch("data_access.HttpRequestProcessor.request_processor")
    def test_with_http_header_content_type_when_post_a_file(self, mock_request_processor):
        """ http header-file [content-type] should be omitted"""
        # Mock an IO stream for the file
        file_content = b"file content"
        file_stream = IO()
        file_stream.write(file_content)
        file_stream.seek(0)
        photo_payload = {'photo' : file_stream}

        mock_processor = patch('data_access.HttpRequestProcessor.request_processor').start()
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data.post({
                'no_resi' : '5563',
                'item' : 'Casing android phone',
            }, 'post-multipart.php', http_header, photo_payload)
        mock_processor.assert_called_once_with(HttpRequestData(endpoint_url='http://localhost.com/smart_drop_box/post-multipart.php', 
                                                               method='post', 
                                                               header={}, 
                                                               data={'no_resi': '5563', 'item': 'Casing android phone'}, 
                                                               param=None, 
                                                               file=photo_payload, 
                                                               time_out=1)
                                                ,TEST_GENERATED_TOKEN)

    def test_with_no_endpoint(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(TypeError):
            http_header = {'content-type' : 'application/json'}
            data.post(payload={'no_resi' : '0230 '},
                      http_header = http_header)


class TestHttpDataAccessUpdateMethod(HelpMockMethod):

    def test_with_correct_data(self):
        self.help_mock_api_response(204, "Resource updated successfully" )
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'multipart/form-data'}
        data_retrieved = data.update({
                'no_resi' : '5563',
                'item' : 'Casing android phone',
                }, 'update.php', http_header)
        assert data_retrieved[0] == 204
        assert data_retrieved[1] ==  "The request was successful but there is no content to return."

    def test_with_invalid_payload_type(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Payload argument should be dictionary type !"):
            http_header = {'content-type' : 'application/json'}
            data.update([{
                    'no_resi' : '5563',
                    'item' : 'Casing android phone'}], 'update.php'
                    , http_header)
            
    def test_with_invalid_header_type(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Http header argument should be dictionary type !"):
            http_header = [{'content-type' : 'application/json'}]
            data.update({
                    'no_resi' : '5563',
                    'item' : 'Casing android phone'}, 'update.php'
                    , http_header)
            
    def test_with_not_found_data(self):
        self.help_mock_api_response(404, "Resource was not found" )
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.update({
                'no_resi' : '0000',
                'item' : 'Casing android phone',
                }, 'update.php', http_header)
        assert data_retrieved[0] == 404
        assert data_retrieved[1] ==  "The requested resource could not be found."      

    def test_with_data_does_not_return_json_format(self):
        self.help_mock_api_response(500, 'Internal server error')
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.update({'no_resi' : '0230', 'item':'Buku tulis Sidu'}, 
                                     'update.php', http_header)
        assert data_retrieved[0]  == 500
        assert data_retrieved[1] == "Internal server error"

    def test_with_invalid_request(self):
        self.help_mock_api_response(400, 'Invalid request', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.update({'no_resasdasi' : '0230', 'iteasm':'Bdduku tulis Sidu'}, 
                                     'update.php', http_header)
        assert data_retrieved[0]  == 400
        assert data_retrieved[1] == "The request was invalid or cannot be otherwise served."

    def test_with_unknown_status_code_response(self):
        self.help_mock_api_response(582, 'unknown problem!', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.update({'no_resi' : '0230', 'item':'Buku tulis Sidu'}, 'update.php', http_header)
        # Not in STATUS_MESSAGES Response handler class variable
        assert data_retrieved[0] is not data._http_request._response_handler.STATUS_MESSAGES.keys()
        assert data_retrieved[1] == "582"


class TestHttpDataAccessDeleteMethod(HelpMockMethod):
    
    def test_with_correct_data(self):
        self.help_mock_api_response(204, "Resource deleted successfully" )
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.delete({
                'no_resi' : '5563'}, 'delete.php', http_header)
        assert data_retrieved[0] == 204
        assert data_retrieved[1] ==  "The request was successful but there is no content to return."

    def test_with_invalid_payload_type(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Param argument should be dictionary type !"):
            http_header = {'content-type' : 'application/json'}
            data.delete([{'no_resi' : '5563'}], 'delete.php', http_header)
            
    def test_with_invalid_header_type(self):
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        with pytest.raises(ValueError, match = "Http header argument should be dictionary type !"):
            http_header = [{'content-type' : 'application/json'}]
            data.delete({'no_resi' : '5563'}, 'delete.php',http_header)
            
    def test_with_not_found_data(self):
        self.help_mock_api_response(404, "Resource was not found" )
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.delete({'no_resi' : '0000'}, 'delete.php',
                                     http_header)
        assert data_retrieved[0] == 404
        assert data_retrieved[1] ==  "The requested resource could not be found."      

    def test_with_data_does_not_return_json_format(self):
        self.help_mock_api_response(500, 'Internal server error')
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.delete({'no_resi' : '0230'}, 'delete.php', http_header)
        assert data_retrieved[0]  == 500
        assert data_retrieved[1] == "Internal server error"

    def test_with_invalid_request(self):
        self.help_mock_api_response(400, 'Invalid request', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.delete({'no_resasdasi' : '0230'}, 'delete.php', http_header)
        assert data_retrieved[0]  == 400
        assert data_retrieved[1] == "The request was invalid or cannot be otherwise served."

    def test_with_unknown_status_code_response(self):
        self.help_mock_api_response(582, 'unknown problem!', True)
        data = HttpDataAccess(
            TEST_URL,
            TEST_GENERATED_TOKEN
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.delete({'no_resi' : '0230'}, 'delete.php', http_header)
        # Not in STATUS_MESSAGES Response handler class variable
        assert data_retrieved[0] is not data._http_request._response_handler.STATUS_MESSAGES.keys()
        assert data_retrieved[1] == "582"


class TestRequestsWithLateSetAuthHeader(HelpMockMethod):
    """ Test the requests when auth header setted lately """

    def test_get_with_token_in_http_header(self):
        """ get request in auth mode """
        test_payload = {
            'no_resi' : '0230',
            'item' : 'sapu lidi',
        }
        self.help_mock_api_response(200, test_payload, True)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json',
                       'authorization' : TEST_GENERATED_TOKEN}
        data.get({'no_resi' : '0230 '}, 'get', http_header)
        assert data._token == TEST_GENERATED_TOKEN
    
    def test_get_with_no_token_in_http_header(self):
        """ get request in no auth mode """
        test_payload = {
            'no_resi' : '0230',
            'item' : 'sapu lidi',
        }
        self.help_mock_api_response(200, test_payload, True)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json'}
        data.get({'no_resi' : '0230 '}, 'get', http_header)
        assert data._token == None

    def test_post_with_token_in_http_header(self):
        """ post request in auth mode """
        test_payload = "success posted in server"
        self.help_mock_api_response(204, test_payload, False)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json',
                       'authorization' : TEST_GENERATED_TOKEN}
        data.post({'no_resi' : '0230 ',
                   'item':'rokok',
                   'date_ordered': '2023'}, 'post.php', http_header)
        assert data._token == TEST_GENERATED_TOKEN
    
    def test_post_with_no_token_in_http_header(self):
        """ post request in no auth mode """
        test_payload = " Successfully posted in server "
        self.help_mock_api_response(204, test_payload, False)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json'}
        data.post({'no_resi' : '0230 ',
                   'item':'rokok',
                   'date_ordered': '2023'}, 'post.php', http_header)
        assert data._token == None

    def test_update_with_token_in_http_header(self):
        """ update request in auth mode """
        test_payload = "success updated old data "
        self.help_mock_api_response(204, test_payload, False)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json',
                       'authorization' : TEST_GENERATED_TOKEN}
        data_retrieved = data.update({
                'no_resi' : '5563',
                'item' : 'Casing android phone',
                }, 'update.php', http_header)
        assert data._token == TEST_GENERATED_TOKEN
    
    def test_update_with_no_token_in_http_header(self):
        """ update request in no auth mode """
        test_payload = " Successfully update old data "
        self.help_mock_api_response(204, test_payload, False)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.update({
                'no_resi' : '5563',
                'item' : 'Casing android phone',
                }, 'update.php', http_header)
        assert data._token == None

    def test_delete_with_token_in_http_header(self):
        """ update request in auth mode """
        test_payload = "success deleted data "
        self.help_mock_api_response(204, test_payload, False)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json',
                       'authorization' : TEST_GENERATED_TOKEN}
        data_retrieved = data.delete({
                'no_resi' : '5563'}, 'delete.php', http_header)
        assert data._token == TEST_GENERATED_TOKEN
    
    def test_delete_with_no_token_in_http_header(self):
        """ update request in no auth mode """
        test_payload = " Successfully deleted data "
        self.help_mock_api_response(204, test_payload, False)
        data = HttpDataAccess(
            TEST_URL,
        )
        http_header = {'content-type' : 'application/json'}
        data_retrieved = data.update({
                'no_resi' : '5563'}, 'delete.php', http_header)
        assert data._token == None
