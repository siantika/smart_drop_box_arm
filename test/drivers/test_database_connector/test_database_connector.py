'''
    Tests:
    1. Get data
    2. Post Data
    3. Update data
    4. Delete data
    5. return status code for each methods

'''
from unittest.mock import patch
import sys
import pytest
sys.path.append('drivers/database_connector')

from database_connector import DatabaseConnector

TEST_URL        = 'http://localhost.com/smart_drop_box/'
TEST_GET_URL    = 'http://localhost.com/smart_drop_box/get.php'
TEST_URL_POST   = 'http://localhost.com/smart_drop_box/post.php'
TEST_UPDATE_URL = 'http://localhost.com/smart_drop_box/update.php'
TEST_DELETE_URL = 'http://localhost.com/smart_drop_box/delete.php'

SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

test_header_const = {'Content-type':'application/json', 'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw'}
test_endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php',
                       'success_items' : 'success_items.php'}

### Test Group init method
class TestDatabaseConInit:

    def help_mock_database_connector(self):
        self.mock_generate_token = patch('database_connector.DatabaseConnector.encode').start()

    def stop_all_patch():
        patch.stopall()


    def test_base_url_should_raise_value_error_when_it_not_ended_with_slash(self):
        try:
            db = DatabaseConnector('http://localhost.com/smart_drop_box', test_endpoint_paths)
        except ValueError as err:
            assert str(err) == "base url should end with '/' !"
        else:
            assert False


    def test_init_process_should_be_correct(self):
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        assert db._base_url == 'http://localhost.com/smart_drop_box/'
        assert isinstance(db._base_url, str)
        assert hasattr(db, '_secret_key')
        assert hasattr(db, '_token_type')
        assert hasattr(db, '_base_url')
        assert hasattr(db, '_algo')
        assert hasattr(db, '_endpoints_urls')

        # initialize encode variable and it has to be '' string!
        assert db._algo == ''
        assert db._token_type == ''
        assert db._secret_key == ''
        assert db._auth_header == ''
        assert isinstance(db._secret_key, str)
        assert isinstance(db._algo, str)
        assert isinstance(db._token_type, str)
        assert isinstance(db._auth_header, str)
        assert isinstance(db._endpoints_urls, dict)
        assert db._endpoints_urls == \
                                                {'get':'get.php',
                                                'update':'update.php',
                                                'delete':'delete.php',
                                                'post':'post.php'}


    def test_url_raise_an_value_error_when_inserted_other_data_type_than_string(self):
        try:    
            db = DatabaseConnector(1212315315, test_endpoint_paths)
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
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db.get_data(param = 'id', value = '1')

        self.mock_requests_get.assert_called_once_with(TEST_GET_URL, params={'id' : '1'}, headers={'Content-type':'application/json'}, timeout=1.0)

        self.stop_all_patch()


    def test_get_data_from_database_should_raise_value_error_when_params_called_with_another_type_than_str(self):
        self.help_mock_requests_methods()
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        try:
            db.get_data(param = id, value = 1)
        except ValueError as ve:
            assert str(ve) == 'Parameters must be String!'
        else:
            assert False

        self.stop_all_patch()

    def test_get_data_should_return_tuple_data_type(self):
        self.help_mock_requests_methods()
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        _result = db.get_data(param = 'id', value = '2')

        assert isinstance(_result, tuple)
        self.stop_all_patch()


    ### STATUS CODE ERROR TESTING
    def test_get_data_from_database_should_return_data_content_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 200
        self.mock_requests_get.return_value.text = "{'id' : '1'}"
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result = db.get_data(param = 'id', value = '1')

        assert _response == 200
        assert _result == "{'id' : '1'}"
        
        self.stop_all_patch()


    def test_get_data_from_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 400
        self.mock_requests_get.return_value.text = "The request was invalid or cannot be otherwise served."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        _response, _result = db.get_data(param = 'id3', value = '1')

        assert _response == 400
        assert _result == "The request was invalid or cannot be otherwise served."

        self.stop_all_patch()


    def test_get_data_from_database_should_return_NO_DATA_FOUND_String_when_status_code_is_404(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 404
        self.mock_requests_get.return_value.text = "The requested resource could not be found."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        _response, _result = db.get_data(param = 'id', value = '10002')

        assert _response == 404
        assert _result == "The requested resource could not be found."

        self.stop_all_patch()


    def test_get_data_from_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 500
        self.mock_requests_get.return_value.text = "Internal server error."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        _response, _result = db.get_data(param = 'id', value = '1')

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
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            db._auth_header =  "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"    
            mock_dumps.return_value ={"name": "sd card", "no_resi": "4931"}
            db.post_data({'name' : 'sd card',  'no_resi' : '4931'}, endpoint= 'post')

            mock_dumps.assert_called_once_with({"name": "sd card", "no_resi": "4931"})
            self.mock_requests_post.assert_called_once_with(TEST_URL_POST, data={"name": "sd card", "no_resi": "4931"}, headers=test_header_const, files = {}, timeout=1.0)
            
        self.stop_all_patch()


    def test_post_data_should_return_tuple_type(self):
        self.help_mock_requests_methods()
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ={"name": "sd card", "no_resi": "4931"}
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            _result = db.post_data({"name": "sd card", "no_resi": "4931"}, endpoint= 'post')

            assert isinstance(_result, tuple)
        
        self.stop_all_patch()


    def test_post_data_to_database_should_handle_multiple_param(self):
        self.help_mock_requests_methods()
        
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = '{"name"="sd card", "no_resi"="4931", "image"="sd_card_img.jpg"}'
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            db._auth_header =  "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"    
            db.post_data({'name':'sd card', 'no_resi':'4931', 'image':'sd_card_img.jpg'}, endpoint= 'post')
            self.mock_requests_post.assert_called_with(TEST_URL_POST, data = '{"name"="sd card", "no_resi"="4931", "image"="sd_card_img.jpg"}', headers=test_header_const, files={}, timeout=1.0)
        
        self.stop_all_patch()

    ### STATUS CODE ERROR TESTING
    def test_post_data_to_database_should_return_the_data_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 200
        self.mock_requests_post.return_value.text = "Data Posted Successfully"
        with patch('json.dumps') as mock_dumps, patch('json.loads') as mock_loads:
            mock_dumps.return_value ='{"name": "sd card", "no_resi": "4931"}'
            mock_loads.return_value = {'data' :'Data Posted Successfully'}
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)

            _response, _result  = db.post_data('{"name": "sd card", "no_resi": "4931"}', endpoint= 'post')

        assert _response == 200
        assert _result   == "Data Posted Successfully"
        
        self.stop_all_patch()


    def test_post_data_to_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 400
        self.mock_requests_post.return_value.text = "The request was invalid or cannot be otherwise served."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ='{"name": "sd card", "no_resi": "4931"}'
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)

            _response, _result  = db.post_data({"name": "sd card", "no_resi": "4931"}, endpoint= 'post')

        assert  _response == 400
        assert  _result   == "The request was invalid or cannot be otherwise served."
        
        self.stop_all_patch()


    def test_post_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 500
        self.mock_requests_post.return_value.text = "Internal server error."
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value ='{"name": "sd card", "no_resi": "4931"}'
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)

            _response, _result  = db.post_data({"name": "sd card", "no_resi": "4931"}, endpoint= 'post')

        assert _response == 500
        assert _result  == "Internal server error."
        
        self.stop_all_patch()


    def test_post_data_should_handle_post_data_without_photo_correctly(self):
        self.help_mock_requests_methods()
        test_data = {"name" : "Arduino", "no_resi" : "2256", "photo" : "asdsadsa"}
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = test_data
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            db.post_data(test_data, endpoint='post')

            self.mock_requests_post.assert_called_once_with(
                (TEST_URL+ "post.php"), data = test_data, headers = {'Content-type':'application/json', 'Authorization' : ''}, files = {}, timeout = 1.0 
            )

    
    def test_post_shoukd_handle_post_data_with_payload_photo_correctly(self):
        self.help_mock_requests_methods()
        test_data = {"name" : "Arduino", "no_resi" : "2256", "photo" : ('kurir_image.jpg', 0x5f)}
        expected_payload = {"name" : "Arduino", "no_resi" : "2256"}
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = test_data
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            db.post_data(test_data, endpoint='success_items')

            self.mock_requests_post.assert_called_once_with(
                (TEST_URL+ "success_items.php"), data = expected_payload, headers = {'Authorization' : ''}, files = {"photo" : ('kurir_image.jpg', 0x5f)}, timeout = 1.0 
            )
    
    def test_post_should_raise_key_error_when_endpoints_is_success_items_and_key_photo_is_not_available(self):
        self.help_mock_requests_methods()
        test_data = {"name" : "Arduino", "no_resi" : "2256"}
        with patch('json.dumps') as mock_dumps, pytest.raises(KeyError, match = "Photo data is missing!"):
            mock_dumps.return_value = test_data
            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            db.post_data(test_data, endpoint='success_items')


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

            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            db._auth_header = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
            db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )
            self.mock_requests_patch.assert_called_once_with(TEST_UPDATE_URL, data = { 'id':'2','name':'Trafo 5 ampere','no_resi':'4623'}, headers=test_header_const, timeout=1.0) 
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

            db = DatabaseConnector(TEST_URL, test_endpoint_paths)
            _result = db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )

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

            db = DatabaseConnector(TEST_URL, test_endpoint_paths)

            _response, _result  = db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )

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

            db = DatabaseConnector(TEST_URL, test_endpoint_paths)

            _response, _result  = db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )

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

            db = DatabaseConnector(TEST_URL,test_endpoint_paths)

            _response, _result  = db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )

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

            db = DatabaseConnector(TEST_URL,test_endpoint_paths)

            _response, _result  = db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )

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

            db = DatabaseConnector(TEST_URL, test_endpoint_paths)

            _response, _result  = db.update_data({
                'id':'2',
                'name':'Trafo 5 ampere',
                'no_resi':'4623'
            }  )

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
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        try:
            db.delete_data(param = id, value = 1)
        except ValueError as ve:
            assert str(ve) == 'Parameters must be String!'
        else:
            assert False

        self.stop_all_patch()


    def test_get_data_should_return_tuple_data_type(self):
        self.help_mock_requests_methods()
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)

        _result = db.delete_data(param = 'id', value = '1')

        assert isinstance(_result, tuple)
        self.stop_all_patch()


    def test_delete_data_should_invoke_delete_method_in_requests_lib_correctly(self):
        self.help_mock_requests_methods()
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db._auth_header = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        db.delete_data(param = 'id', value = '4')
        self.mock_requests_patch.assert_called_once_with(TEST_DELETE_URL, params={'id':'4'}, headers = test_header_const, timeout=1.0)


     ### STATUS CODE ERROR TESTING
    def test_delete_data_to_database_should_return_DATA_DELETED_SUCCESSFULLY_when_status_code_is_204(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 204
        self.mock_requests_patch.return_value.text = "The request was successful but there is no content to return."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

        assert _response == 204
        assert _result  == "The request was successful but there is no content to return."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_NO_DATA_FOUND_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 404
        self.mock_requests_patch.return_value.text = "The requested resource could not be found."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

        assert _response == 404
        assert _result  == "The requested resource could not be found."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_BAD_REQUEST_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 400
        self.mock_requests_patch.return_value.text = "The request was invalid or cannot be otherwise served."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

        assert _response == 400
        assert _result  == "The request was invalid or cannot be otherwise served."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_METHOD_NOT_ALLOWED_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 405
        self.mock_requests_patch.return_value.text = "Method Not Allowed."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

        assert _response == 405
        assert _result  == "Method Not Allowed."
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 500
        self.mock_requests_patch.return_value.text = "Internal server error."
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

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
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

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
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
   
        _response, _result  = db.delete_data(param = 'id', value = '4')

        assert _response == 401
        assert _result  == "No Authorization."
        
        self.stop_all_patch()

### Test cases for Tokenize methods
class TestToken:
    def help_mock_jwt_method(self):
        self.mock_jwt_encode = patch('jwt.encode').start()

    def stop_all_patch(self):
        patch.stopall()

    def test_generate_token_should_invoke_method_correctly(self):
        self.help_mock_jwt_method()
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db.set_encode(
            secret = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1', 
            algo = 'HS256',
            token_type ='Bearer',
        )
        db.encode(
            payload_data =
                {
                "name":"sian",
                "email":"sian@mediavimana@gmail.com"
                }
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


    def test_encode_should_return_correctly(self):
        '''
            Should return string contained 'type of token ['Bearer', 'auth', etc] and jwt token.
        '''
        self.help_mock_jwt_method()
        _return_token_utf8 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.mock_jwt_encode.return_value = _return_token_utf8.encode('utf-8')
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db.set_encode(
            secret = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1', 
            algo = 'HS256',
            token_type ='Bearer',
        )
        _ret_val = db.encode(
            payload_data =
                {
                "name":"sian",
                "email":"sian@mediavimana@gmail.com"
                }
        )

        assert isinstance(_ret_val, str)
        assert _ret_val == "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.stop_all_patch()

    def test_encode_should_set_auth_header_class_attrib_correctly(self):
        self.help_mock_jwt_method()
        _return_token_utf8 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.mock_jwt_encode.return_value = _return_token_utf8.encode('utf-8')
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db.set_encode(
            secret = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1', 
            algo = 'HS256',
            token_type ='Bearer',
        )
        _ret_val = db.encode(
            payload_data =
                {
                "name":"sian",
                "email":"sian@mediavimana@gmail.com"
                }
        )

        assert db._auth_header == "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.stop_all_patch()

    def test_set_encode_should_be_correct(self):
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db.set_encode(
            secret     = SECRET_KEY_LOCAL,
            algo       = 'HS256',
            token_type = 'Bearer',
        )

        assert db._secret_key == SECRET_KEY_LOCAL
        assert db._algo  == 'HS256'
        assert db._token_type == 'Bearer'

    def test_reset_encode_should_be_correct(self):
        self.help_mock_jwt_method()
        _return_token_utf8 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
        self.mock_jwt_encode.return_value = _return_token_utf8.encode('utf-8')
        db = DatabaseConnector(TEST_URL, test_endpoint_paths)
        db.set_encode(
            secret     = SECRET_KEY_LOCAL,
            algo       = 'HS256',
            token_type = 'Bearer',
        )
        db.encode(
            payload_data =
                {
                "name":"sian",
                "email":"sian@mediavimana@gmail.com"
                }
        )

        db.reset_encode()

        assert db._secret_key == ''
        assert db._algo  == ''
        assert db._token_type == ''
        assert db._auth_header == ''
