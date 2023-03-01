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
sys.path.append('drivers/database_connector')
from database_connector import DatabaseConnector

TEST_URL = 'http:// localhost.com'
TEST_URL_POST = 'http://localhost.com/data_no_resi'
TEST_PATCH_URL = 'http://localhost.com'
TEST_DELETE_URL = 'http://localhost.com/delete'



class TestDatabaseCon:

    def test_init_process_should_be_correct(self):
        database_con = DatabaseConnector(TEST_URL)
        assert database_con._url == 'http:// localhost.com'
        assert isinstance(database_con._url, str)

    def test_init_url_raise_an_value_error_when_inserted_other_data_type_than_string(self):
        try:    
            database_con = DatabaseConnector(1212315315)
        except ValueError as ve:
            assert str(ve) == 'url is not valid data type, use string instead!'
        else:
            assert False



class TestDatabaseConGetData:

    def help_mock_requests_methods(self):
        self.mock_requests_get = patch('requests.get').start()

    def stop_all_patch(self):
        patch.stopall()

    def test_get_data_from_database_should_invoke_get_method_from_requests_lib_and_timeout_is_1_sec(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL)
        database_con.get_data(param = 'no_resi', value = 1)

        self.mock_requests_get.assert_called_once_with(TEST_URL, data={'no_resi' : '1'}, timeout=1.0)

        self.stop_all_patch()
    
    def test_get_data_from_database_should_return_the_data_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_get.return_value.status_code = 200
        self.mock_requests_get.return_value.text = b"['2021', '4256', '8891']"
        database_con = DatabaseConnector(TEST_URL)
   
        _ret_value = database_con.get_data(param = 'no_resi', value = 1)

        assert database_con._response.status_code == 200
        assert _ret_value == "['2021', '4256', '8891']"
        
        self.stop_all_patch()


    def test_get_data_from_database_should_return_NO_DATA_FOUND_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_URL)
        self.mock_requests_get.return_value.status_code = 400
        self.mock_requests_get.return_value.text = b"Bad Request"

        _ret_value = database_con.get_data(param = 'no_resi', value = 1)

        assert database_con._response.status_code == 400
        assert _ret_value == "Bad Request"

        self.stop_all_patch()


    def test_get_data_from_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_URL)
        self.mock_requests_get.return_value.status_code = 500
        self.mock_requests_get.return_value.text = b"Server Error"

        _ret_value = database_con.get_data(param = 'no_resi', value = 1)

        assert database_con._response.status_code == 500
        assert _ret_value == "Server Error"

        self.stop_all_patch()



class TestDatabaseConPostData:

    def help_mock_requests_methods(self):
        self.mock_requests_post = patch('requests.post').start()

    def stop_all_patch(self):
        patch.stopall()


    def test_post_data_to_database_should_invoke_post_method_from_requests_lib_and_get_arg_as_data_to_be_sent(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL_POST)
        database_con.post_data(param='data', value = '4931')
        self.mock_requests_post.assert_called_once_with(TEST_URL_POST, data = {'data':'4931'})
        self.stop_all_patch()


    def test_post_data_to_database_should_handle_multiple_param(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_URL_POST)

        database_con.post_data(param='data', value = '4391')
        self.mock_requests_post.assert_called_with(TEST_URL_POST, data = {'data':'4391'})
       
        database_con.post_data(param='no_resi', value = '0203')
        self.mock_requests_post.assert_called_with(TEST_URL_POST, data = {'no_resi':'0203'})
        
        database_con.post_data( param='image',value='FFF58E')
        self.mock_requests_post.assert_called_with(TEST_URL_POST, data = {'image':'FFF58E'})
        
        self.stop_all_patch()

    ### STATUS CODE ERROR TESTING
    def test_post_data_to_database_should_return_the_data_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_post.return_value.status_code = 200
        database_con = DatabaseConnector(TEST_URL)
   
        _ret_value = database_con.post_data(param='no_resi', value = '45454')

        assert database_con._response.status_code == 200
        assert _ret_value == "Data Posted"
        
        self.stop_all_patch()


    def test_post_data_to_database_should_return_NO_DATA_FOUND_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_URL)
        self.mock_requests_post.return_value.status_code = 400
        self.mock_requests_post.return_value.text = b"Bad Request"

        _ret_value = database_con.post_data(param='no_resi', value = '45454')

        assert database_con._response.status_code == 400
        assert _ret_value == "Bad Request"

        self.stop_all_patch()


    def test_post_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_URL)
        self.mock_requests_post.return_value.status_code = 500
        self.mock_requests_post.return_value.text = b"Server Error"

        _ret_value = database_con.post_data(param='no_resi', value = '45454')

        assert database_con._response.status_code == 500
        assert _ret_value == "Server Error"

        self.stop_all_patch()



class TestDatabaseConPatchData:
    
    def help_mock_requests_methods(self):
        self.mock_requests_patch = patch('requests.patch').start()


    def stop_all_patch(self):
        patch.stopall()


    def test_patch_data_should_invoke_patch_method_from_requests_lib_correclty(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_PATCH_URL)

        database_con.patch_data(param_matching = 'id', param_matching_value = '2', param_patched = 'no_resi', param_patched_value = '9969')

        assert database_con._url_for_patch == TEST_PATCH_URL + '/id' + '/2'
        self.mock_requests_patch.assert_called_once_with(TEST_PATCH_URL + '/id' +'/2', data = {'no_resi' : '9969'})   

        self.stop_all_patch() 

    ### STATUS CODE ERROR TESTING
    def test_patch_data_to_database_should_return_DATA_PATCHED_when_status_code_is_200(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 200
        database_con = DatabaseConnector(TEST_URL)
   
        _ret_value = database_con.patch_data(param_matching = 'id', param_matching_value = '2', param_patched = 'no_resi', param_patched_value = '9969')

        assert database_con._response.status_code == 200
        assert _ret_value == "Data Patched"
        
        self.stop_all_patch()


    def test_patch_data_to_database_should_return_NO_DATA_FOUND_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_URL)
        self.mock_requests_patch.return_value.status_code = 400
        self.mock_requests_patch.return_value.text = b"Bad Request"

        _ret_value = database_con.patch_data(param_matching = 'id', param_matching_value = '2', param_patched = 'no_resi', param_patched_value = '9969')

        assert database_con._response.status_code == 400
        assert _ret_value == "Bad Request"

        self.stop_all_patch()


    def test_patch_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_URL)
        self.mock_requests_patch.return_value.status_code = 500
        self.mock_requests_patch.return_value.text = b"Server Error"

        _ret_value = database_con.patch_data(param_matching = 'id', param_matching_value = '2', param_patched = 'no_resi', param_patched_value = '9969')

        assert database_con._response.status_code == 500
        assert _ret_value == "Server Error"

        self.stop_all_patch()



class TestDatabaseConDeleteData:

    def help_mock_requests_methods(self):
        self.mock_requests_patch = patch('requests.delete').start()


    def stop_all_patch(self):
        patch.stopall()


    def test_delete_data_should_invoke_delete_method_in_requests_lib_correctly(self):
        self.help_mock_requests_methods()
        database_con = DatabaseConnector(TEST_DELETE_URL)

        database_con.delete_data(param = 'no_resi', value = '9969')

        self.mock_requests_patch.assert_called_once_with(TEST_DELETE_URL, data = {'no_resi' : '9969'})

     ### STATUS CODE ERROR TESTING
    def test_delete_data_to_database_should_return_DATA_DELETED_when_status_code_is_204(self):
        self.help_mock_requests_methods()
        self.mock_requests_patch.return_value.status_code = 204
        database_con = DatabaseConnector(TEST_DELETE_URL)
   
        _ret_value = database_con.delete_data(param = 'no_resi', value = '9969')

        assert database_con._response.status_code == 204
        assert _ret_value == "Data Deleted"
        
        self.stop_all_patch()


    def test_delete_data_to_database_should_return_NO_DATA_FOUND_String_when_status_code_is_400(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_DELETE_URL)
        self.mock_requests_patch.return_value.status_code = 400
        self.mock_requests_patch.return_value.text = b"Bad Request"

        _ret_value = database_con.delete_data(param = 'no_resi', value = '9969')

        assert database_con._response.status_code == 400
        assert _ret_value == "Bad Request"

        self.stop_all_patch()


    def test_delete_data_to_database_should_return_SERVER_ERROR_String_when_status_code_is_500(self):
        self.help_mock_requests_methods()

        database_con = DatabaseConnector(TEST_DELETE_URL)
        self.mock_requests_patch.return_value.status_code = 500
        self.mock_requests_patch.return_value.text = b"Server Error"

        _ret_value = database_con.delete_data(param = 'no_resi', value = '9969')

        assert database_con._response.status_code == 500
        assert _ret_value == "Server Error"

        self.stop_all_patch()