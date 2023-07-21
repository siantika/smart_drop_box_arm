"""
This module provides classes and utilities for data access via HTTP requests 
to a specified API.

Classes:
- DataAccess (ABC): Abstract base class for manipulating data 
  (post, get, update, and delete) 
  from a source (database, API, etc).
- HttpRequestData (dataclass): Represents the necessary data for an HTTP request.
- HttpRequestProcessor: Handles making HTTP requests and processing responses.
- ResponseHandler: Handles processing HTTP responses.
- HttpDataAccess (DataAccess): Handles data access via HTTP requests to a specified API.

Modules:
- dataclasses: Provides the 'dataclass' decorator for creating classes with 
  special methods for attribute handling.
- json: Provides functions for working with JSON data.
- os: Provides functions for interacting with the operating system.
- sys: Provides access to some variables used or maintained by the interpreter 
  and to functions that interact with the interpreter.
- urllib.parse: Provides functions to parse URLs and work with URIs.
- abc: Abstract Base Classes (ABC) support for defining abstract base classes.
- requests: HTTP library for Python.
- typing: Support for type hints.
- log: A custom logger module from the 'utils' package.

Note:
- The 'DataAccess' class is an abstract base class that defines the interface for 
  manipulating data from various sources. Subclasses must implement the abstract  
  methods 'get', 'post', 'update', and 'delete' to perform specific data operations.
- The 'HttpDataAccess' class is a concrete implementation of 'DataAccess' 
  that specifically handles data access through HTTP requests. It utilizes 
  the 'HttpRequestProcessor' to make HTTP requests and the 'ResponseHandler' 
  to process the responses.

For usage and detailed documentation, please refer to the individual class docstrings.
"""
from dataclasses import dataclass
import json
import os
import sys
from urllib.parse import urljoin
from abc import ABC, abstractmethod
import requests
from typing import IO
import logging

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'utils'))
import log

class DataAccess(ABC):
    """Abstract base class for manipulating data 
       (post, get, update, and delete) from a source 
       (database, API, etc).
    """
    @abstractmethod
    def get(self, param: dict, destination: any) -> tuple[int, dict]:
        """get(param: dict) -> tuple[int, dict]: 
           Retrieves data based on the provided parameters."""
        pass

    @abstractmethod
    def post(self, payload: dict, destination: any) -> tuple[int, dict]:
        """post(payload: dict) -> tuple[int, dict]: 
           Creates new data with the given payload."""
        pass

    @abstractmethod
    def update(self, payload: dict, destination: any) -> tuple[int, dict]:
        """ update(payload: dict) -> tuple[int, dict]: 
            Updates existing data using the provided payload."""
        pass

    @abstractmethod
    def delete(self, payload: dict, destination: any) -> tuple[int, dict]:
        """ delete(param: dict) -> tuple[int, dict]: Deletes data based on 
            the specified parameters."""
        pass


@dataclass
class HttpRequestData:
    """Data class representing the necessary data for an HTTP request.

    Attributes:
    - endpoint_url (str): The URL of the API endpoint.
    - method (str): The HTTP method to be used (e.g., 'get', 'post', 'update', 'delete', etc.).
    - header (dict): Dictionary containing HTTP request headers.
    - data (json, optional): JSON data to be sent in the request body (for POST and UPDATE methods).
    - param (dict, optional): Dictionary containing parameters for the request 
      (for GET and DELETE methods).
    - file (dict[str, IO], optional): Dictionary of file data (key-value pairs) 
      for multipart/form-data requests.
    - time_out (int, optional): The timeout value for the request.
    """
    endpoint_url: str
    method: str
    header: dict
    data: json = None
    param: dict[str, any] = None
    file: dict[str, tuple[any, IO]] = None
    time_out: int = None


class HttpRequestProcessor:
    """Handles making HTTP requests and processing responses."""

    def __init__(self) -> None:
        self._response_handler = ResponseHandler()

    def request_processor(self, request: HttpRequestData, log:logging.Logger = None,
                          auth_header: str = None) -> tuple[int, str]:
        """Makes an HTTP request using the provided HttpRequestData and 
           an optional authorization header.

        Args:
        - request (HttpRequestData): Data for the HTTP request.
        - auth_header (str, optional): Authorization header to be included in the request.
        - log (log.Logger): provide logging feature for notify the absence of auth token.
                            Default is None/off
        
        Returns:
        A tuple containing the HTTP status code and the response data or error message (if any).
        """
        if log:
            request.header['Authorization'] = auth_header if auth_header is not None \
                else log.warning("Your request is not authorized!")
        else:
            request.header['Authorization'] = auth_header
        try:
            response = requests.request(
                method=request.method,
                url=request.endpoint_url,
                params=request.param,
                data=request.data,
                files=request.file,
                headers=request.header,
                timeout=request.time_out
            )
            return self._response_handler.return_response(response)
        except requests.exceptions.ConnectionError as error:
            return (503, str(error))


class ResponseHandler:
    """Handles processing HTTP responses."""
    STATUS_CODE_RETURNING_DATA = [200, 201]
    STATUS_MESSAGES = {
        500: "Internal server error",
        444: "Server blocked the request.",
        404: "The requested resource could not be found.",
        400: "The request was invalid or cannot be otherwise served.",
        204: "The request was successful but there is no content to return.",
        405: "Method Not Allowed.",
        403: "Access forbidden!",
        401: "No Authorization.",
    }

    @staticmethod
    def _decode_json_data(response_data: json) -> dict[str:any] | str:
        """ Convert received-data to python object (dictionary) """
        try:
            return json.loads(response_data)
        except json.decoder.JSONDecodeError:
            return "Error: API does not return correct JSON format!"

    def _handle_returning_data(self, response: requests.Response) -> str:
        " Handling the server returning data contents"
        return self._decode_json_data(response.text)

    def _handle_status_code_response(self, response: requests.Response) -> str:
        """ Handling status code from requests based on library maker.
            I created the common status code and it's content. Preventing
            from bad API returns.

        """
        status_code = response.status_code
        return self.STATUS_MESSAGES.get(status_code, str(status_code))

    def return_response(self, response: requests.Response) -> tuple[int, any]:
        """Processes the HTTP response and returns the status code and response data.

        Args:
        - response (requests.Response): The HTTP response object.

        Returns:
        A tuple containing the HTTP status code and the processed response data.
        If the status code indicates an error, the response data contains 
        the corresponding error message.
        """
        if response.status_code in self.STATUS_CODE_RETURNING_DATA:
            return (response.status_code, self._handle_returning_data(response))
        return (response.status_code, self._handle_status_code_response(response))


class HttpDataAccess(DataAccess):
    """Handles data access via HTTP requests to a specified API.

    Attributes:
    - base_url (str): The base URL of the API.
    - endpoint_urls (dict): Dictionary containing endpoint names 
      as keys and their corresponding URLs as values.
    - token (str, optional): Authorization token to be used in the HTTP requests.
    """

    def __init__(self, base_url: str, endpoint_urls: dict, token: str = None) -> None:
        """Initializes the HttpDataAccess object.
        Args:
        - base_url (str): The base URL of the API.
        - endpoint_urls (dict): Dictionary containing endpoint names as keys and 
          their corresponding URLs as values.
        - token (str, optional): Authorization token to be used in the HTTP requests.
        """
        if not base_url.endswith('/'):
            raise ValueError("base url should end with '/' !")

        self._base_url = base_url
        self._endpoints_urls = endpoint_urls
        self._token = token
        self._http_request = HttpRequestProcessor()

    def _make_full_url_endpoint(self, endpoint: str):
        """ Make a full url for specific endpoint"""
        if endpoint not in self._endpoints_urls:
            raise KeyError(f"{endpoint} is not in endpoint urls dict! ")
        return urljoin(self._base_url, self._endpoints_urls[endpoint])

    def _check_arguments_type(self, param=None, payload=None, http_header=None):
        " Check the existance of args in CRUD method"
        if param is not None:
            if not isinstance(param, dict):
                raise ValueError("Param argument should be dictionary type !")
        if payload is not None:
            if not isinstance(payload, dict):
                raise ValueError(
                    "Payload argument should be dictionary type !")
        if http_header is not None:
            if not isinstance(http_header, dict):
                raise ValueError(
                    "Http header argument should be dictionary type !")

    def get(self, param: dict, endpoint: str, http_header: dict = None,
            time_out: int = 1) -> tuple[int, str]:
        """Makes a GET request to retrieve data based on the provided parameters.

        Args:
        - param (dict): Dictionary containing parameters for the GET request.
        - http_header (dict, optional): Dictionary of HTTP headers to be included in the request.
        - endpoint (str) : the endpoint of specific API

        Returns:
        A tuple containing the HTTP status code and the response data or error message (if any).
        """
        self._check_arguments_type(param=param, http_header=http_header)
        http_data = HttpRequestData(
            endpoint_url=self._make_full_url_endpoint(endpoint),
            method='get',
            header=http_header,
            param=param,
            time_out=time_out
        )
        return self._http_request.request_processor(http_data, self._token)

    def post(self, payload: dict, endpoint: str, http_header: dict = None,
             file: dict[str, IO] = None, time_out: int = 1) -> tuple[int, str]:
        """Makes a POST request to create new data with the given payload.

        Args:
        - payload (dict): Dictionary containing data to be sent in the request body.
        - http_header (dict, optional): Dictionary of HTTP headers to be included in the request.
        - file (dict[str, tuple[any,IO], optional): Dictionary of file data (key-value pairs) 
          for multipart/form-data requests.
        - endpoint (str) : the endpoint of specific API

        Returns:
        A tuple containing the HTTP status code and the response data or error message (if any).
        """
        self._check_arguments_type(payload=payload, http_header=http_header)
        # We should ommit the header-file (content-type) in http header if we use multipart type.
        # data (payload) should be a dict type.
        if file is not None:
            http_header.pop('content-type', None)
        else:
            payload = json.dumps(payload)
        http_data = HttpRequestData(
            endpoint_url=self._make_full_url_endpoint(endpoint),
            method='post',
            header=http_header,
            data=payload,
            file=file,
            time_out=time_out
        )
        return self._http_request.request_processor(http_data, self._token, log)

    def update(self, payload: dict, endpoint: str, http_header: dict = None,
               time_out: int = 1) -> tuple[int, str]:
        """Makes a PATCH request to update existing data using the provided payload.
        Args:
        - payload (dict): Dictionary containing data to be sent in the request body for updating.
        - http_header (dict, optional): Dictionary of HTTP headers to be included in the request.
        - endpoint (str) : the endpoint of specific API

        Returns:
        A tuple containing the HTTP status code and the response data or error message (if any).
        """
        self._check_arguments_type(payload=payload, http_header=http_header)
        json_payload = json.dumps(payload)
        http_data = HttpRequestData(
            endpoint_url=self._make_full_url_endpoint(endpoint),
            method='patch',
            header=http_header,
            data=json_payload,
            time_out=time_out
        )
        return self._http_request.request_processor(http_data, self._token,log)

    def delete(self, param: dict, endpoint=None, http_header: dict = None,
               time_out: int = 1) -> tuple[int, str]:
        """Makes a DELETE request to delete data based on the specified parameters.

        Args:
        - param (dict): Dictionary containing parameters for the DELETE request.
        - http_header (dict, optional): Dictionary of HTTP headers to be included in the request.
        - endpoint (str) : the endpoint of specific API

        Returns:
        A tuple containing the HTTP status code and the response data or error message (if any).
        """
        self._check_arguments_type(param=param, http_header=http_header)
        http_data = HttpRequestData(
            endpoint_url=self._make_full_url_endpoint(endpoint),
            method='delete',
            header=http_header,
            param=param,
            time_out=time_out
        )
        return self._http_request.request_processor(http_data, self._token,log)
