'''
    Tests:
    1. Get data
    2. Post Data
    3. Update data
    4. Delete data
    5. return status code for each methods

'''
from unittest.mock import patch, Mock
import sys
sys.path.append('drivers/database_connector')
from database_connector import DatabaseConnector
import requests

TEST_URL = 'http:// localhost.com'
TEST_URL_POST = 'http://localhost.com/data_no_resi'
TEST_PATCH_URL = 'http://localhost.com/update.php'
TEST_DELETE_URL = 'http://localhost.com/delete'


### Test Group init method
class TestDatabaseConInit:

    def test_init_process_should_be_correct(self):
        database_con = DatabaseConnector(TEST_URL)
        assert database_con._url == 'http:// localhost.com'
        assert isinstance(database_con._url, str)


    def test_init_url_raise_an_value_error_when_inserted_other_data_type_than_string(self):
        try:    
            database_con = DatabaseConnector(1212315315)
        except ValueError as ve:
            assert str(ve) == 'url must be String!'
        else:
            assert False


### Test Group Get_Data method
class TestDatabaseConGetData:

    def help_mock_requests_methods(self):
        self.mock_requests_get = patch('requests.get').start()
    

    def stop_all_patch(self):
        patch.stopall()


    def test_get_data_from_database_should_invoke_get_method_from_requests_lib(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL)
        database_con.get_data(param = 'id', value = '1')

        self.mock_requests_get.assert_called_once_with(TEST_URL, params={'id' : '1'}, headers={'content-type':'application/json'}, timeout=1.0)

        self.stop_all_patch()


    def test_get_data_from_database_should_raise_value_error_when_params_called_with_another_type_than_str(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL)

        try:
            database_con.get_data(param = id, value = 1)
        except ValueError as ve:
            assert str(ve) == 'Parameters must be String!'
        else:
            assert False

        self.stop_all_patch()

    def test_get_data_should_return_tuple_data_type(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL)

        _result = database_con.get_data(param = 'id', value = '2')

        assert isinstance(_result, tuple)
        self.stop_all_patch()


    ### STATUS CODE ERROR TESTING
    def test_get_data_from_database_should_return_data_content_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 200
        self.mock_requests_get.return_value.text = "{'id' : '1'}"
        database_con = DatabaseConnector(TEST_URL)
   
        _response, _result = database_con.get_data(param = 'id', value = '1')

        assert _response == 200
        assert _result == "{'id' : '1'}"
        
        self.stop_all_patch()


    def test_get_data_from_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 400
        self.mock_requests_get.return_value.text = "The request was invalid or cannot be otherwise served."
        database_con = DatabaseConnector(TEST_URL)

        _response, _result = database_con.get_data(param = 'id3', value = '1')

        assert _response == 400
        assert _result == "The request was invalid or cannot be otherwise served."

        self.stop_all_patch()


    def test_get_data_from_database_should_return_NO_DATA_FOUND_String_when_status_code_is_404(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 404
        self.mock_requests_get.return_value.text = "The requested resource could not be found."
        database_con = DatabaseConnector(TEST_URL)

        _response, _result = database_con.get_data(param = 'id', value = '10002')

        assert _response == 404
        assert _result == "The requested resource could not be found."

        self.stop_all_patch()


    def test_get_data_from_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 500
        self.mock_requests_get.return_value.text = "Internal server error."
        database_con = DatabaseConnector(TEST_URL)

        _response, _result = database_con.get_data(param = 'id', value = '1')

        assert _response == 500
        assert _result == "Internal server error."

        self.stop_all_patch()


### Test Group Post_Data method
class TestDatabaseConPostData:

    def help_mock_requests_methods(self):
        self.mock_requests_post = patch('requests.post').start()
    
    
    def stop_all_patch(self):
        patch.stopall()


    '''
        NOTE: json.dumps should be mocked with instruction 'with' otherwise, it wouldn't work!    
    '''
    def test_post_data_to_database_should_invoke_post_method_from_requests_lib_and_get_arg_as_data_to_be_sent(self):
        self.help_mock_requests_methods()
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ={"name": "sd card", "no_resi": "4931"}

            database_con = DatabaseConnector(TEST_URL_POST)
            database_con.post_data(name = 'sd card',  no_resi = '4931')

            mock_dumps.assert_called_once_with({"name": "sd card", "no_resi": "4931"})
            self.mock_requests_post.assert_called_once_with(TEST_URL_POST, data={"name": "sd card", "no_resi": "4931"}, headers={'content-type': 'application/json'}, timeout=1.0)
            
        self.stop_all_patch()


    def test_post_data_should_return_tuple_type(self):
        self.help_mock_requests_methods()
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ={"name": "sd card", "no_resi": "4931"}

            database_con = DatabaseConnector(TEST_URL_POST)
            _result = database_con.post_data(name = 'sd card',  no_resi = '4931')

            assert isinstance(_result, tuple)
        
        self.stop_all_patch()


    def test_post_data_to_database_should_handle_multiple_param(self):
        self.help_mock_requests_methods()
        
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = '{"name"="sd card", "no_resi"="4931", "image"="sd_card_img.jpg"}'
            database_con = DatabaseConnector(TEST_URL_POST)

            database_con.post_data(name='sd card', no_resi='4931', image='sd_card_img.jpg')
            self.mock_requests_post.assert_called_with(TEST_URL_POST, data = '{"name"="sd card", "no_resi"="4931", "image"="sd_card_img.jpg"}', headers={'content-type': 'application/json'}, timeout=1.0)
        
        self.stop_all_patch()


    ### STATUS CODE ERROR TESTING
    def test_post_data_to_database_should_return_the_data_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 200
        self.mock_requests_post.return_value.text = "Data Posted Successfully"
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ='{"name": "sd card", "no_resi": "4931"}'
            database_con = DatabaseConnector(TEST_URL_POST)

            _response, _result  = database_con.post_data(param='no_resi', value = '45454')

        assert _response == 200
        assert _result   == "Data Posted Successfully"
        
        self.stop_all_patch()


    def test_post_data_to_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 400
        self.mock_requests_post.return_value.text = "The request was invalid or cannot be otherwise served."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ='{"name": "sd card", "no_resi": "4931"}'
            database_con = DatabaseConnector(TEST_URL_POST)

            _response, _result  = database_con.post_data(param='no_resi', value = '45454')

        assert  _response == 400
        assert  _result   == "The request was invalid or cannot be otherwise served."
        
        self.stop_all_patch()


    def test_post_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 500
        self.mock_requests_post.return_value.text = "Internal server error."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ='{"name": "sd card", "no_resi": "4931"}'
            database_con = DatabaseConnector(TEST_URL_POST)

            _response, _result  = database_con.post_data(param='no_resi', value = '45454')

        assert _response == 500
        assert _result  == "Internal server error."
        
        self.stop_all_patch()


### Test Group Update_Data method
class TestDatabaseConUpdateData:
    
    def help_mock_requests_methods(self):
        self.mock_requests_patch = patch('requests.patch').start()
    
    
    def stop_all_patch(self):
        patch.stopall()


    def test_update_data_should_invoke_update_method_from_requests_lib_correclty(self):
        self.help_mock_requests_methods()
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)

            database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

            self.mock_requests_patch.assert_called_once_with(TEST_PATCH_URL, data = { 'id':'2','name':'Trafo 5 ampere','no_resi':'4623'}, headers={'content-type':'application/json'}, timeout=1.0) 
            mock_dumps.assert_called_once_with({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            })  

        self.stop_all_patch() 


    def test_update_data_should_return_string_type(self):
        self.help_mock_requests_methods()
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)
            _result = database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

            assert isinstance(_result, tuple)

        self.stop_all_patch()       


    ### STATUS CODE ERROR TESTING
    def test_update_data_to_database_should_return_DATA_PATCHED_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 200
        self.mock_requests_patch.return_value.text = "Item updated successfully"
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)

            _response, _result  = database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

        assert _response == 200
        assert _response, _result  == "Item updated successfully"
        
        self.stop_all_patch()


    def test_update_data_to_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 400
        self.mock_requests_patch.return_value.text = "The request was invalid or cannot be otherwise served."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)

            _response, _result  = database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

        assert _response == 400
        assert _response, _result  == "The request was invalid or cannot be otherwise served."
        
        self.stop_all_patch()


    def test_update_data_to_database_should_return_NO_DATA_FOUND_String_when_status_code_is_404(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 404
        self.mock_requests_patch.return_value.text = "The requested resource could not be found."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)

            _response, _result  = database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

        assert _response == 404
        assert _response, _result  == "The requested resource could not be found."
        
        self.stop_all_patch()


    def test_update_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 500
        self.mock_requests_patch.return_value.text = "The server encountered an unexpected condition that prevented it from fulfilling the request."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)

            _response, _result  = database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

        assert _response == 500
        assert _response, _result  == "The server encountered an unexpected condition that prevented it from fulfilling the request."
    
        self.stop_all_patch()


    def test_update_data_to_database_should_return_METHOD_NOT_ALLOWED_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 405
        self.mock_requests_patch.return_value.text = "Method Not Allowed."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = {
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  

            database_con = DatabaseConnector(TEST_PATCH_URL)

            _response, _result  = database_con.update_data(param_matching = 'id', param_matching_value = '2', name = 'Trafo 5 ampere', no_resi = '4623')

        assert _response == 405
        assert _response, _result  == "Method Not Allowed."
        self.stop_all_patch()


### Test Group Delete_Data method
class TestDatabaseConDeleteData:

    def help_mock_requests_methods(self):
        self.mock_requests_patch = patch('requests.delete').start()


    def stop_all_patch(self):
        patch.stopall()


    def test_delete_data_from_database_should_raise_value_error_when_params_called_with_another_type_than_str(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_DELETE_URL)

        try:
            database_con.delete_data(param = id, value = 1)
        except ValueError as ve:
            assert str(ve) == 'Parameters must be String!'
        else:
            assert False

        self.stop_all_patch()


    def test_get_data_should_return_tuple_data_type(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL)

        _result = database_con.delete_data(param = 'id', value = '1')

        assert isinstance(_result, tuple)
        self.stop_all_patch()


    def test_delete_data_should_invoke_delete_method_in_requests_lib_correctly(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_DELETE_URL)

        database_con.delete_data(param = 'id', value = '4')

        self.mock_requests_patch.assert_called_once_with(TEST_DELETE_URL, params={'id':'4'}, timeout=1.0)


     ### STATUS CODE ERROR TESTING
    def test_delete_data_to_database_should_return_DATA_DELETED_SUCCESSFULLY_when_status_code_is_204(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 204
        self.mock_requests_patch.return_value.text = "The request was successful but there is no content to return."
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 204
        assert _result  == "The request was successful but there is no content to return."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_NO_DATA_FOUND_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 404
        self.mock_requests_patch.return_value.text = "The requested resource could not be found."
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 404
        assert _result  == "The requested resource could not be found."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 400
        self.mock_requests_patch.return_value.text = "The request was invalid or cannot be otherwise served."
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 400
        assert _result  == "The request was invalid or cannot be otherwise served."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_METHOD_NOT_ALLOWED_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 405
        self.mock_requests_patch.return_value.text = "Method Not Allowed."
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 405
        assert _result  == "Method Not Allowed."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 500
        self.mock_requests_patch.return_value.text = "Internal server error."
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 500
        assert _result  == "Internal server error."
        
        self.stop_all_patch()


### Mock the response HTTP 
class TestResponseServer:
    def help_mock_requests_methods(self):
        self.mock_requests_patch = patch('requests.delete').start()

    def stop_all_patch(self):
        patch.stopall()

    def test_response_should_return_FORBIDDEN_when_status_code_is_403(self):
        '''
            I Use delete method, it doesn't matter to use another methods, since I only want
            to know the response code only.
        
        '''
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 403
        self.mock_requests_patch.return_value.text = "Access forbidden!"
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 403
        assert _result  == "Access forbidden!"
        
        self.stop_all_patch()

    def test_response_should_return_NO_AUTH_when_status_code_is_401(self):
        '''
            I Use delete method, it doesn't matter to use another methods, since I only want
            to know the response code only.
        
        '''
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 401
        self.mock_requests_patch.return_value.text = "No Authorization."
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _response, _result  = database_con.delete_data(param = 'id', value = '4')

        assert _response == 401
        assert _result  == "No Authorization."
        
        self.stop_all_patch()

###
class TestGenerateToken:
    def help_mock_jwt_method(self):
        self.mock_jwt_encode = patch('jwt.encode').start()

    def stop_all_patch(self):
        patch.stopall()

    def test_generate_token_should_invoke_method_correctly(self):
        self.help_mock_jwt_method()
        db = DatabaseConnector(TEST_URL)
        db.encode(
            payload_data =
                {
                "name":"sian",
                "email":"sian@mediavimana@gmail.com"
                },
            secret = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1', 
            algo = 'HS256',
            token_type='Bearer',
        )

        self.mock_jwt_encode.assert_called_once_with(
            payload={
                "name":"sian",
                "email":"sian@mediavimana@gmail.com",
            },
            key = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1',
            algorithm = 'HS256',
            headers = {'typ':'JWT'},
        )

        self.stop_all_patch()


    def test_generate_token_should_return_correctly(self):
        '''
            Should return string contained 'type of token ['Bearer', 'auth', etc] and jwt token.
        '''
        self.help_mock_jwt_method()
        _return_token_utf8 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.mock_jwt_encode.return_value = _return_token_utf8.encode('utf-8')
        db = DatabaseConnector(TEST_URL)
        _ret_val = db.encode(
            payload_data =
                {
                "name":"sian",
                "email":"sian@mediavimana@gmail.com"
                },
            secret = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1', 
            algo = 'HS256',
            token_type='Bearer',
        )

        assert isinstance(_ret_val, str)
        assert _ret_val == "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.stop_all_patch()


