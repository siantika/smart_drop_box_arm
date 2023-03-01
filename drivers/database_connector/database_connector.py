'''
    File           : database_connector.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 
    
    This code helps to performing transactional data in DBMS. It has standard CRUD features (Create, Read, Update, and Delete).
    It returns status code for operation performed in text (string). No need to perform singleton because 'requests' library
    has it's own method to handle this.

    It has similar arguments for each methods (Except: patch_data). Those are:
        @param <str> --> the parameter of end point url. eg: no_resi.
        @value <str> --> the value of parameter of end point url. eg:'9969'

    NOTE:
        Testing in local database

    Example code:
        see: './example/drivers/database_connector_ex.py' file!

    License: see 'licenses.txt' file in the root of project
'''
import requests

class DatabaseConnector:

    def __init__(self, url:str):
        self._url = url
        if not isinstance(self._url, str):
            raise ValueError('url is not valid data type, use string instead!')
        

    def _help_return_response_requests(self, response : requests, method : str):
        _status_code = response.status_code
        if _status_code == 400:
            return 'Bad Request'
        elif _status_code == 500:
            return 'Server Error'
        elif _status_code == 200:
            if method == 'GET':
                return response.text.decode('utf-8')
            elif method == 'POST':
                return 'Data Posted'
            elif method == 'PATCH':
                return 'Data Patched'
        elif _status_code == 204:
            if method == 'DELETE':
                return 'Data Deleted'
            

    def get_data(self, param:str, value:str):
        payload = {str(param) : str(value)}
        self._response = requests.get(self._url, data = payload, timeout=1.0)
        _status_code = self._help_return_response_requests(self._response, 'GET')
        return _status_code
        

    def post_data(self, param:str, value:str):         
        payload = {str(param): str(value)}
        self._response = requests.post(self._url, data = payload)
        _status_code = self._help_return_response_requests(self._response, 'POST')
        return _status_code
        

    '''
        Desc    : Patch data according parameter_matching. We search the intended data (@parameter_patched : @value_patched) by
                  looking to another parameters (@param_matching : @param_matching_value)
        Params  :
                    @param_matching         --> parameter in url end point for base to patch other param
                    @param_matching_value   --> the value of matching parameter
                    @param_patched          --> the parameter that we want to patch
                    @param_patched_value    --> the value that we want to patch
        Case Ex. : I have a table in database named 'items'. It looks like below:
                     ------------------------------
                    | id | name_of_item | no_resi  | 
                     ------------------------------
                    | 1  | solder 60 W  |   4958   |
                    | 2  | arduino uno  |   8968   |
                    | 3  | breadboard   |   2312   |
                     ------------------------------

                    I want to patch the arduino uno's no resi, so I will code:
                        '' ******************************************* ''
                            patch_data(
                                     param_matching = 'name_of_item', 
                                     param_matching_value = 'arduino uno', 
                                     param_patched = 'no_resi', 
                                     param_patched_value = '5555'
                                     )
                        '' ******************************************* ''
                    So, I changed no resi of arduino uno to be '5555'. We can use 'id' as matching parameter too!

    '''
    def patch_data(self, param_matching:str, param_matching_value:str, param_patched:str, param_patched_value:str):
        self._url_for_patch = self._url + '/' + param_matching + '/' + param_matching_value
        payload = {param_patched : param_patched_value}
        self._response = requests.patch(self._url_for_patch, data = payload)
        _status_code = self._help_return_response_requests(self._response, 'PATCH')
        return _status_code
    

    def delete_data(self, param:str, value:str):
        payload = {param:value}
        self._response = requests.delete(self._url, data = payload)
        _status_code = self._help_return_response_requests(self._response, 'DELETE')
        return _status_code