"""
    File           : database_connector.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

    Example code:
        see: './example/drivers/database_connector_ex.py' file!

    License: see 'licenses.txt' file in the root of project
"""

import json
import sys
from urllib.parse import urljoin
import jwt
import requests

# Please refers to json data from server and see the key contains the data intended!
KEY_DATA_IN_GET_METHOD = 'data'
REQUEST_TIMEOUT = 60.0 # secs

class DatabaseConnector:
    """
        This is a class that performing database transcations.

        This class performs database transactions with API server. It performs CRUD 
        (create, read, update, delete) in database. 

        Attributes:
            base_url (str)       : base url server.
            endpoint_url (dict)  : enpoints API relative from base_url.
                                   eg: {
                                        'post'   : 'url relative from base_url',
                                        'get'    : 'idem',
                                        'update' : 'idem',
                                        'delete' : 'idem',
                                    }
                                    keys should be specified like that!


        This class uses 'requests' library. It uses 'requests' methods for perfoming CRUD.
        The class needs base url and enpoint paths. These attributes will be specifying 
        the particular API endpoints needed by methods (update, get, delete, and update).

        Post and Update method use dict arg attributes (key:val), in the other hand, get and
        delete use params.

        Preventing from server error, it handles by returning status code 503 and response = "Server
        Unavailable" (hard coded because the API in dynamic).

        NOTE: If server reqiures authorization, you need to invoke set_encode and 
              encode respectively! (default: no auth)

    """

    def __init__(self, base_url: str, endpoint_url:dict):
        if not isinstance(base_url, str):
            raise ValueError('url must be String!')
        if not base_url.endswith('/'):
            raise ValueError("base url should end with '/' !")
        self._base_url = base_url
        self._algo = ''
        self._token_type = ''
        self._secret_key = ''
        self._auth_header = ''
        self._endpoints_urls = endpoint_url

    def _help_return_response_requests(self, response: requests) -> str:
        """
            This function help to returns the message base on status code from server.

            Args:
                response (request) : Object method called in CRUD methods.

            Returns:
                str: message operation result.
        """
        _message = None
        _status_code = response.status_code
        if _status_code == 500:
            _message = "Internal server error."
        elif _status_code == 404:
            _message = "The requested resource could not be found."
        elif _status_code == 400:
            _message = "The request was invalid or cannot be otherwise served."
        elif _status_code == 204:
            _message = "The request was successful but there is no content to return."
        elif _status_code == 201:
            _message == "Success created a data in server!"
        # NOTE: Please concern this code when API GET is changed! and the return code is 200
        elif _status_code == 200:
            _data_raw = response.text # it contains row data in dict
            '''
                We handle the wrong data (maybe API programer did wrong type while writing json data)
                by returning error json decoder to response!
            '''
            try:
                _decoded_data = json.loads(_data_raw)
            except json.decoder.JSONDecodeError as msg_error:
                _message = "API data does not retrun correct JSON format!"
            else:
                if KEY_DATA_IN_GET_METHOD not in _decoded_data:
                    _message = "Success but not returned data"
                else:
                    _message =  _decoded_data[KEY_DATA_IN_GET_METHOD]

        elif _status_code == 405:
            _message = "Method Not Allowed."
        elif _status_code == 403:
            _message = "Access forbidden!"
        elif _status_code == 401:
            _message = "No Authorization."
        else:
            _message = _status_code  # returns uncovered message
        return _message

    def get_data(self, param: str, value: str) -> tuple:
        """
            This function get a data in database base on parameter (key-val argument).

            Args:
                param (str) : Parameter for searching a database's params in endpoint url.
                value (str) : Value of parameter

            Returns:
                tuple: response status code and result message of operation.
        """
        _status_code = None
        _result = None
        if not isinstance(param, str) and not isinstance(value, str):
            raise ValueError('Parameters must be String!')
        
        _get_path = self._endpoints_urls['get']
        _full_get_path = urljoin(self._base_url, _get_path)
        _parameters = {param: value}
        _header = {'content-type': 'application/json',
                   'Authorization': f'{self._auth_header}'}
        
        try:
            _response = requests.get(
                _full_get_path, params=_parameters, headers=_header, timeout=REQUEST_TIMEOUT)
            _status_code = _response.status_code
            _result = self._help_return_response_requests(_response)
        except requests.exceptions.ConnectionError:
            _status_code = 503
            _result = "Server Unavailable"
        finally:
            return _status_code, _result

    def post_data(self, data:dict, endpoint:str) -> tuple:
        """
            This function post data to database base on user defined payload to specific endpoints.

            Args:
                data (dict) :  User defined parameters and values for post data in endpoint url.
                endpoints   :  Endpoint from server

            Returns:
                tuple: response status code and result message of operation.
        """
        _full_post_path = ""
        _header = {}
        _payload = {}
        _file = {}
        _status_code = None
        _response = None 


        _post_path = self._endpoints_urls[endpoint]
        #check endpoints
        if _post_path == 'post.php':    
            _full_post_path = urljoin(self._base_url, _post_path)
            _payload   = json.dumps(data)
            _header    = {'Content-type': 'application/json',
                            'Authorization': f'{self._auth_header}'}
            _file      = {}
        
        #this endpoint is specific in smart drop app, It uses mutipart-form-data.
        #so we don't need to make payload as json. We send the photo through FILES and
        # other data in POST.
        elif _post_path == 'success_items.php':
            #parsing data photo
            if not 'photo' in data:
                raise KeyError("Photo data is missing!")
            
            _file      = {"photo" : data['photo']}
            # Payload should not contain photo bin data!
            del data['photo']
            _full_post_path = urljoin(self._base_url, _post_path)
            _payload   = data
            _header    = {'Authorization': f'{self._auth_header}'}

        try:    
            _response  = requests.post(
                _full_post_path, data =_payload, headers=_header, files=_file, timeout=REQUEST_TIMEOUT)
            _result    = self._help_return_response_requests(_response)
        except requests.exceptions.ConnectionError:
            _status_code = 503
            _result = "Server Unavailable"
        finally:
            return _status_code, _result


    def update_data(self, data:dict) -> tuple:
        '''
            Update data base on key-value args parameters

            Args:
                data (dict)   : parameters and values for update endpoint url.

            Returns:
                tuple: response status code and result message of operation.
        '''
        _status_code = None 
        _response = None
        # Create full path url for update data
        _update_path = self._endpoints_urls['update']
        _full_update_path = urljoin(self._base_url, _update_path)
        # Encode data to JSON
        _payload = json.dumps(data)
        # create auth header
        _header = {'content-type': 'application/json',
                   'Authorization': f'{self._auth_header}'}
        # Make update request to server
        try:
            _response = requests.patch(
                _full_update_path, data=_payload, headers=_header, timeout=REQUEST_TIMEOUT)
            _result = self._help_return_response_requests(_response)
        except requests.exceptions.ConnectionError:
            _status_code = 503
            _result = "Server Unavailable"
        return _status_code, _result
    

    def delete_data(self, param: str, value: str) -> tuple:
        """
            This function delete a single row data in database base on parameter (key-value) args.

            Args:
                param (str): Parameter for searching database's params in endpoint url.
                value (str): The value of parameter.

            Returns:
                tuple: response status code and result message of operation.
        """
        _status_code = None 
        _response = None

        if not isinstance(param, str) and not isinstance(value, str):
            raise ValueError('Parameters must be String!')
        _delete_path = self._endpoints_urls['delete']
        _full_delete_path = urljoin(self._base_url, _delete_path)
        _payload = {param: value}
        _headers = {'content-type': 'application/json',
                    'Authorization': f'{self._auth_header}'}
        
        try:
            _response = requests.delete(
                _full_delete_path, params=_payload, headers=_headers, timeout=REQUEST_TIMEOUT)
            _result = self._help_return_response_requests(_response)
        except requests.exceptions.ConnectionError:
            _status_code = 503
            _result = "Server Unavailable"
        return _status_code, _result


    def encode(self, payload_data: dict = {}) -> str:
        """
            This function encodes data as JWT token. The encoded data  from
            JWT. Encoding produces a byte-string data, so we need decode it.

            Args:
                payload (dict)  : Payload in HTTP header

            Returns:
                str: Authorization header data 
        """
        _encoded_data = jwt.encode(
            payload=payload_data,
            key=self._secret_key,
            algorithm=self._algo,
            headers={'typ': 'JWT'}
        )

        # only decode when python version is below 3.8.10
        python_version = sys.version_info
        if python_version <= (3, 9, 0):
            _decoded_to_utf8 = _encoded_data.decode("utf-8") 
            _tokenized = f"{self._token_type} {_decoded_to_utf8}"
        else:
            _tokenized = f"{self._token_type} {_encoded_data}"
            
            
        # set auth_header class attribute
        self._auth_header = _tokenized
        return _tokenized
    

    def set_encode(self, secret: str, algo: str, token_type: str) -> None:
        """
            This function sets the encode class attributes.

            Args:
                secret  (str)   : Your secret key to perform encoding data
                algo    (str)   : Algorithm for encoding data
                token_type (str): The type of token --> eg. Bearer,Auth,etc

            Returns:
                None
        """
        self._secret_key = secret
        self._algo = algo
        self._token_type = token_type

    def reset_encode(self) -> None:
        """
            This function clears attributes class regard encoding methods.

            Args:
                -

            Returns:
                None
        """
        self._secret_key = ''
        self._algo = ''
        self._token_type = ''
        self._auth_header = ''
