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
from urllib.parse import urljoin
import jwt
import requests

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
                                    keys should be specify like that!


        This class uses 'requests' library. It uses 'requests' methods for perfoming CRUD.
        The class needs base url and enpoint paths. These attributes will be specifying 
        the particular API endpoints needed by methods (update, get, delete, and update).

        Post and Update method use dict arg attributes (key:val), in the other hand, get and
        delete use params.

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
        _get_path = self._endpoints_urls['get']
        _full_get_path = urljoin(self._base_url, _get_path)
        _parameters = {param: value}
        print(self._base_url)
        print(_full_get_path)
        _header = {'content-type': 'application/json'}
        _response = requests.get(
            _full_get_path, params=_parameters, headers=_header, timeout=1.0)
        _result = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def post_data(self, data:dict) -> tuple:
        """
            This function post data to database base on user defined parameter (key-val argument).

            Args:
                data (dict) :  User defined parameters and values for post data in endpoint url.

            Returns:
                tuple: response status code and result message of operation.
        """
        _post_path = self._endpoints_urls['post']
        _full_post_path = urljoin(self._base_url, _post_path)
        _payload   = json.dumps(data)
        _header    = {'content-type': 'application/json',
                          'Authorization': f'{self._auth_header}'}
        _response  = requests.post(
            _full_post_path, data =_payload, headers=_header, timeout=1.0)
        _result    = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def update_data(self, data:dict) -> tuple:
        '''
            Update data base on key-value args parameters

            Args:
                data (dict)   : parameters and values for update endpoint url.

            Returns:
                tuple: response status code and result message of operation.
        '''
        # Create full path url for update data
        _update_path = self._endpoints_urls['update']
        _full_update_path = urljoin(self._base_url, _update_path)
        # Encode data to JSON
        _payload = json.dumps(data)
        # create auth header
        _header = {'content-type': 'application/json',
                   'Authorization': f'{self._auth_header}'}
        # Make update request to server
        _response = requests.patch(
            _full_update_path, data=_payload, headers=_header, timeout=1.0)
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
        _delete_path = self._endpoints_urls['delete']
        _full_delete_path = urljoin(self._base_url, _delete_path)
        _payload = {param: value}
        _headers = {'content-type': 'application/json',
                    'Authorization': f'{self._auth_header}'}
        _response = requests.delete(
            _full_delete_path, params=_payload, headers=_headers, timeout=1.0)
        _result = self._help_return_response_requests(_response)
        return _response.status_code, _result

    def encode(self, payload_data: dict) -> str:
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
