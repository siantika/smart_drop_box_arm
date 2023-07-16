"""
    File           : database_connector.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

    Example code:
        see: './example/drivers/database_connector_ex.py' file!

    License: see 'licenses.txt' file in the root of project
"""

from dataclasses import dataclass
import json
import os
import sys
from urllib.parse import urljoin
from abc import ABC, abstractmethod
import jwt
import requests
from typing import IO

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'utils'))
import log

# Please refers to json data from server and see the key contains the data intended!
KEY_DATA_IN_GET_METHOD = 'data'
REQUEST_TIMEOUT = 60.0 # secs
#Added user-agent header (MUST)
user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

from abc import ABC, abstractmethod

class DataAccess(ABC):
    """Represents manipulating data (post, get, update, and delete) from a source (database, API, etc)."""

    @abstractmethod
    def get(self, **kwargs) -> tuple[int, dict]:
        """
        Get data from the data source based on the provided parameters.

        This method is meant to retrieve data from a data source using the given
        parameters and their corresponding values to search for matching data.

        Args:
            **kwargs (dict): Keyword arguments representing the search criteria.
                The keys are parameter names, and the values are the search values.

        Returns:
            tuple[int, dict]: A tuple containing the status code and a response dictionary.
                The status code represents the result of the operation (e.g., 200 for success).
                The response dictionary may contain the retrieved data based on the search criteria.

        Example:
            To retrieve data with parameters 'param1' and 'value1':
            >>> result_status, result_data = get(param1='value1')
        """
        pass

    @abstractmethod
    def post(self, **kwargs) -> tuple[int, dict]:
        """
        Create a new entry in the data source with the provided payload.

        This method is meant to create a new entry in the data source using the provided payload.

        Args:
            **kwargs (dict): Keyword arguments representing the data for the new entry.
                The keys are field names, and the values are the data to be added.

        Returns:
            tuple[int, dict]: A tuple containing the status code and a response dictionary.
                The status code represents the result of the operation (e.g., 201 for success).
                The response dictionary may contain additional information about the created entry.

        Example:
            To create a new entry with data for 'field1' and 'field2':
            >>> result_status, result_data = post(field1='data1', field2='data2')
        """
        pass

    @abstractmethod
    def update(self, **kwargs) -> tuple[int, dict]:
        """
        Update an existing entry in the data source.

        This method is meant to update an existing entry in the data source based on
        some predefined criteria or conditions.

        Args:
            **kwargs (dict): Keyword arguments representing the data for the updated entry.
                The keys are field names, and the values are the new data to be updated.

        Returns:
            tuple[int, dict]: A tuple containing the status code and a response dictionary.
                The status code represents the result of the operation (e.g., 200 for success).
                The response dictionary may contain additional information about the updated entry.

        Example:
            To update an existing entry with new data for 'field1' and 'field2':
            >>> result_status, result_data = update(field1='new_data1', field2='new_data2')
        """
        pass

    @abstractmethod
    def delete(self, **kwargs) -> tuple[int, dict]:
        """
        Delete an existing entry from the data source.

        This method is meant to delete an existing entry from the data source based on
        some predefined criteria or conditions.

        Args:
            **kwargs (dict): Keyword arguments representing the search criteria for deletion.
                The keys are parameter names, and the values are the search values.

        Returns:
            tuple[int, dict]: A tuple containing the status code and a response dictionary.
                The status code represents the result of the operation (e.g., 204 for success).
                The response dictionary may contain additional information about the deleted entry.

        Example:
            To delete entries where 'param1' equals 'value1':
            >>> result_status, result_data = delete(param1='value1')
        """
        pass



class HttpAuthorization():
    def __init__(self, secret:str, 
                 algorithm:str, 
                 token_type:str) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._token_type = token_type
        
    def _generate_auth_header(self):
        return jwt.encode(
            self._secret,
            self._algorithm,
            headers={'typ': 'JWT'}
        )
    
    def get_auth_header(self)-> str:
        """ Returns a correct format for token according python version """
        token = self._generate_auth_header()
        python_ver = sys.version_info
        if python_ver <= (3,9,0):
            decoded_token = token.decode("utf-8")
            auth_header = f"{self._token_type} {decoded_token}"
        else:
            auth_header = f"{self._token_type} {token}"

        return auth_header
        
        

class HttpHeaderConstruction:
    def __init__(self) -> None:
        header = { 
            'content-type' : 'application/json',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        }



class MakeHttpRequest:
    def make_generic_request(self, endpoint_url:str, 
                            method:str, header:HttpHeaderConstruction,
                            data:json = None, param:dict[str,any] = None)-> tuple[int,str]:
        """ Request will be put in URL header (as query/params) 
            Args:
                method (str)  :  a HTTP method [GET or DELETE].
                header (dict) :  The header object for url. Containing auth token.
                param (str)   :  where the data will be caried.
                                    (url or body).
                data (json)   : Data will be sent in body of http
                                and it has to be JSON.
                param (dict)
            Returns:
                response (tuple[int,str]) : response from external API. 
                Status code and request content.
                             
        """
        try:     
            response = requests.request(
                method = method,
                url = endpoint_url,
                params = param,
                data   = data,
                headers = header.header,
                timeout = REQUEST_TIMEOUT
            )
            return response
        except requests.exceptions.ConnectionError as error:
            return (503, str(error))
        
    def make_multipart_request(self, endpoint_url:str, 
                            method:str, header:HttpHeaderConstruction,
                            file:IO, data:json = None)-> tuple[int,str]: 
        try:     
            response = requests.request(
                method = method,
                url = endpoint_url,
                data = data,
                files = file,
                headers = header.header,
                timeout = REQUEST_TIMEOUT
            )
            return response
        except requests.exceptions.ConnectionError as error:
            return (503, str(error))

class HttpDataAccess(DataAccess):
    def __init__(self, base_url: str, endpoint_urls:dict, auth:HttpAuthorization = None):
        if not base_url.endswith('/'):
            raise ValueError("base url should end with '/' !")
        self._base_url = base_url
        self._endpoints_urls = endpoint_urls

        self.header = HttpHeaderConstruction()
    
        if auth is None:
            log.logger.warning("Your data connection is not secure, Try to implement an authorization connection!")
        else:
            auth_header = auth.get_auth_header()
            self.header['Authorization'] = auth_header


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
        elif _status_code == 444:
            _message = "Server block the request"
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

    def get(self, **kwargs) -> tuple[int, str]:
        """  """
        full_path_of_get = urljoin(self._base_url, self._endpoints_urls['get'])    
        try:
            response = requests.get(
                url = full_path_of_get, 
                params = kwargs, 
                headers = self.header,
                timeout = REQUEST_TIMEOUT, 
            )
            return self._help_return_response_requests(response)
        except requests.exceptions.ConnectionError:
            return (503, "Server unavailable!")


    def post_data(self, **kwargs) -> tuple[int, str]:
        _full_post_path = ""
        _header = {}
        _payload = {}
        _file = {}
        _status_code = None
        _response = None 
        _header.update(user_agent)

        _post_path = self._endpoints_urls[endpoint]
        #check endpoints
        if _post_path == 'post.php':    
            _full_post_path = urljoin(self._base_url, _post_path)
            _payload   = json.dumps(data)
            _header    = {'Content-type': 'application/json',
                            'Authorization': f'{self._auth_header}'}
            _header.update(user_agent)
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
        try:    
            _response  = requests.post(
                url = _full_post_path, 
                data = _payload, 
                headers = _header, 
                files = _file, 
                timeout = REQUEST_TIMEOUT)
            return self._help_return_response_requests(_response)
        except requests.exceptions.ConnectionError:
            return (503, "Server Unavailable")



    def update(self, **kwargs) -> tuple[int, str]:
        full_path_of_update = urljoin(self._base_url, self._endpoints_urls['update'])
        payload = json.dumps(kwargs)
        try:
            response = requests.patch(
                url = full_path_of_update, 
                data = payload, 
                headers = self.header, 
                timeout = REQUEST_TIMEOUT
                )
            return self._help_return_response_requests(response)
        except requests.exceptions.ConnectionError:
            return (503, "Server unavailable!")
    

    def delete(self, **kwargs) -> tuple[int, str]:        
        full_path_of_delete = urljoin(self._base_url, self._endpoints_urls['delete'])
        try:
            response = requests.delete(
                url = full_path_of_delete, 
                params = kwargs, 
                headers = self.header, 
                timeout = REQUEST_TIMEOUT)
            return self._help_return_response_requests(response)
        except requests.exceptions.ConnectionError:
            return (503, "Server Unavailable")

