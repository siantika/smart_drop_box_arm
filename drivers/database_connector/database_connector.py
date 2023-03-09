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
import jwt
import requests


class DatabaseConnector:
    """
        This is a class that performing database transcations.

        Here is where you would provide a more detailed description of what the class does,
        what its attributes are, what methods it has, and how they work.
        NOTE: If server reqiures authorization, you need to invoke set_encode and encode respectively!

        This class performs database transaction with API server. It performs CRUD (create, read, update, delete) 
        in database. 

        Attributes:
            url (str)       : url endpoint from server.

        This class uses 'requests' library. It uses 'requests' methods for perfoming CRUD.
        The class method will invoke 'self._url' for specifying the url endpoint. Each method 
        will perform particular operation (get, post, update, and delete) by invoking 'requests'
        methods. Each methods will return status code and message of operation result.

    """

    def __init__(self, url: str):
        if not isinstance(url, str):
            raise ValueError('url must be String!')
        self._url = url
        self._algo = ''
        self._token_type = ''
        self._secret_key = ''
        self._auth_header = ''

    def _help_return_response_requests(self, response: requests) -> str:
        """
            This function help to returns the message base on status code from server.

            Args:
                response (request) : Object method called in CRUD methods.

            Returns:
                str: message operation result.
        """
        _status_code = response.status_code
        if _status_code == 500:
            _message = "Internal server error."
        elif _status_code == 404:
            _message = "The requested resource could not be found."
        elif _status_code == 400:
            _message = "The request was invalid or cannot be otherwise served."
        elif _status_code == 204:
            _message = "The request was successful but there is no content to return."
        elif _status_code == 200:
            _message = response.text
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
        if not isinstance(param, str) and not isinstance(value, str):
            raise ValueError('Parameters must be String!')
        _parameters = {param: value}
        _header = {'content-type': 'application/json'}
        _response = requests.get(
            self._url, params=_parameters, headers=_header, timeout=1.0)
        _result = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def post_data(self, **kwargs) -> tuple:
        """
            This function post data to database base on user defined parameter (key-val argument).

            Args:
                kwargs (dict{(str):(str)}) :  User defined parameters for post data in endpoint url.

            Returns:
                tuple: response status code and result message of operation.
        """
        _payload = json.dumps(kwargs)
        _header = {'content-type': 'application/json',
                   'Authorization': f'{self._auth_header}'}
        _response = requests.post(
            self._url, data=_payload, headers=_header, timeout=1.0)
        _result = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def update_data(self, param_matching: str, param_matching_value: str, **kwargs) -> tuple:
        '''
            Update data according parameter_matching and parameter_value_matching

            Args:
                param_matching (str)          : Parameter in url end point for key to search other params
                param_matching_value  (str)   : The value of matching parameter
                kwargs  (dict{(str):(str)}) : Custom parameters (key-value) define by user

            Returns:
                tuple: response status code and result message of operation.

            Case Ex: 
                I have a table in database named 'items'. It looks like below:
                        ------------------------------
                        | id | name_of_item | no_resi  | 
                        ------------------------------
                        | 1  | solder 60 W  |   4958   |
                        | 2  | arduino uno  |   8968   |
                        | 3  | breadboard   |   2312   |
                        ------------------------------

                        I want to update the arduino uno's no resi, so I will code:
                            '' ******************************************* ''
                            db = DatabaseConnector(url)

                            db.update_data(
                                        param_matching = 'name_of_item', 
                                        param_matching_value = 'arduino uno', 
                                        no_resi = '0023'
                                        )
                            '' ******************************************* ''
                        So, arduino unos no_resi-value updated to be '0023'. We can use 'id' as matching parameter and
                        added another parameters and its value according the API doc.
        '''
        _dict_params = {param_matching: param_matching_value, **kwargs}
        _payload = json.dumps(_dict_params)
        _header = {'content-type': 'application/json',
                   'Authorization': f'{self._auth_header}'}
        _response = requests.patch(
            self._url, data=_payload, headers=_header, timeout=1.0)
        _result = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def delete_data(self, param: str, value: str) -> tuple:
        """
            This function delete a single row data in database base on parameter (key-value) args.

            Args:
                param (str): Parameter for searching database's params in endpoint url.
                value (str): The value of parameter.

            Returns:
                tuple: response status code and result message of operation.
        """

        if not isinstance(param, str) and not isinstance(value, str):
            raise ValueError('Parameters must be String!')
        _payload = {param: value}
        _headers = {'content-type': 'application/json',
                    'Authorization': f'{self._auth_header}'}
        _response = requests.delete(
            self._url, params=_payload, headers=_headers, timeout=1.0)
        _result = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def encode(self, payload_data: dict) -> str:
        """
            This function encodes data as JWT token. The enocded data  from
            JWT.encode produces a byte-string data, so we need decode it.

            Args:
                payload (dict)  : data payload to be encoded

            Returns:
                str: Authorization header data 
        """
        _encoded_data = jwt.encode(
            payload=payload_data,
            key=self._secret_key,
            algorithm=self._algo,
            headers={'typ': 'JWT'}
        )
        _decoded_to_utf8 = _encoded_data.decode('utf-8')
        _tokenized = f"{self._token_type} {_decoded_to_utf8}"
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
            This function clear attributes class regard encoding methods.

            Args:
                -

            Returns:
                None
        """
        self._secret_key = ''
        self._algo = ''
        self._token_type = ''
        self._auth_header = ''
