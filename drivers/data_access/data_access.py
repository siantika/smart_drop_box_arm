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

from abc import ABC, abstractmethod

class DataAccess(ABC):
    """Represents manipulating data (post, get, update, and delete) from a source (database, API, etc)."""
    @abstractmethod
    def get(self, param:dict) -> tuple[int, dict]:
        pass

    @abstractmethod
    def post(self, payload:dict) -> tuple[int, dict]:
        pass

    @abstractmethod
    def update(self, payload:dict) -> tuple[int, dict]:
        pass

    @abstractmethod
    def delete(self, payload:dict) -> tuple[int, dict]:
        pass


class HttpAuthorization(ABC):

    @abstractmethod
    def generate_token(self)-> str:
        pass 
    
    @abstractmethod
    def get_auth_header(self)-> str:
        pass
            

class JwtBearerAuth(HttpAuthorization):
    def __init__(self, secret:str, algorithm:str, 
                 token_type:str) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._token_type = token_type
        
    def generate_token(self, payload_header:dict) -> str:
        return jwt.encode(
            payload = payload_header,
            secret = self._secret,
            algorithm = self._algorithm,
            headers = {'typ' : 'JWT'}
        )
    
    def get_auth_header(self) -> str:
        """ Returns a correct token format according python version """
        token = self.generate_token()
        python_ver = sys.version_info
        if python_ver <= (3,9,0):
            decoded_token = token.decode("utf-8")
            auth_header = f"{self._token_type} {decoded_token}"
        else:
            auth_header = f"{self._token_type} {token}"
        return auth_header
        

@dataclass
class HttpRequestData:
    endpoint_url:str
    method:str
    header:dict
    data:json = None
    param:dict[str, any] = None 
    file:dict[str, IO] = None
    time_out:int = None


class HttpRequestProcessor:
    def request_processor(self, request:HttpRequestData, 
                     auth_header:str = None)-> tuple[int,str]:
        
        # Add auth argument in header
        request.header['Authorization'] = auth_header if auth_header is not None \
        else log.logger.warning("Your request is not authorized!")

        try:     
            response = requests.request(
                method = request.method,
                url = request.endpoint_url,
                params = request.param,
                data   = request.data,
                files = request.file,
                headers = request.header,
                timeout = request.time_out
            )
            return response
        except requests.exceptions.ConnectionError as error:
            return (503, str(error))
        

class HttpDataAccess(DataAccess):
    DEFAULT_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
                Safari/537.3'
    }
    JSON_HEADER = DEFAULT_HEADER.copy()
    MULTIPART_HEADER = DEFAULT_HEADER.copy()
    JSON_HEADER['content-type'] = 'application/json'
    MULTIPART_HEADER['content-type'] = 'multipart/form-data'

    def __init__(self, base_url: str, endpoint_urls:dict, 
                 auth:HttpAuthorization = None) -> None:
        
        if not base_url.endswith('/'):
            raise ValueError("base url should end with '/' !")
        
        self._auth = auth if auth is not None else None
        self._base_url = base_url
        self._endpoints_urls = endpoint_urls
        self._http_request = HttpRequestProcessor()
    
    def _make_full_url_endpoint(self, endpoint:str):
        return urljoin(self._base_url, self._endpoints_urls[endpoint])

    def get(self, param:dict) -> tuple[int, str]:
        http_data = HttpRequestData(
            endpoint_url = self._make_full_url_endpoint('get'),
            method = 'get',
            header = self.JSON_HEADER,
            param = param            
        )
        return self._http_request.request_processor(http_data, self._auth)
      
    def post_data(self, payload:dict, file:dict[str,IO] = None) -> tuple[int, str]:
        json_payload = json.dumps(payload)
        http_data = None       
        if file is not None:
            http_data = HttpRequestData(
                endpoint_url = self._make_full_url_endpoint('post-multipart'),
                method = 'post',
                header = self.MULTIPART_HEADER,
                data = json_payload      
            ) 
        else:
            http_data = HttpRequestData(
                endpoint_url = self._make_full_url_endpoint('post'),
                method = 'post',
                header = self.JSON_HEADER,
                data = json_payload      
            )
        return self._http_request.request_processor(http_data, self._auth)

    def update(self, payload:dict) -> tuple[int, str]:
        json_payload = json.dumps(payload)
        http_data = HttpRequestData(
            endpoint_url = self._make_full_url_endpoint('patch'),
            method = 'patch',
            header = self.JSON_HEADER,
            data =  json_payload      
        )
        self._http_request.request_processor(http_data, self._auth)
    

    def delete(self, param:dict) -> tuple[int, str]:    
        http_data = HttpRequestData(
            endpoint_url = self._make_full_url_endpoint('delete'),
            method = 'delete',
            header = self.JSON_HEADER,
            param = param            
        )
        return self._http_request.request_processor(http_data, self._auth)




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
