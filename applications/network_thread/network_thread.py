'''
    File           : network_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Apr, 2023
    Description    : 

        This code handles requests to API Server from operation thread.
    Data transfer (red: payload) between two threads are mp.Queue 's. 
    It has 2 child classes, GetRequest is for request GET data in server
    (no_resi etc) periodically amd PostRequest is for requests DELETE and POST
    data to server (Delete stored item no_resi and upload success items + photo)   
    
    License: see 'licenses.txt' file in the root of project
'''

import configparser
import os
import sys
import threading
import multiprocessing as mp
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/database_connector'))
sys.path.append(os.path.join(parent_dir, 'utils'))

# should put here due to DIY libs.
from database_connector import DatabaseConnector
import log

full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')

# Endpoints url of API
endpoint_paths = {
    'get': 'get.php', 'update': 'update.php',
    'delete': 'delete.php', 'post': 'post.php',
    'success_items': 'success_items.php'}

# We don't send data in http header, so keep it empty.
# It exists only for content of auth requests.
DEFAULT_PAYLOAD_HEADER = {}
PAYLOAD_GET_DATA = {'method': 'GET', 'payload': {'no_resi': '0'}}

NETWORK_TIMEOUT = 5  # secs


class NetworkThread:
    '''
        Class Network Thread is class that contains methods to run a network thread (make
    request to server).
          It uses database_connector driver lib to perform database transaction. Queue data
    contain payload as dictionary will be parse as 'method' [post, update, delete, get] and
    'payload' contains dictionary data. Method will be used as parameter to perform specific
    transacation from local server. It will return status_code and response from local server
    as tuple type (then we convert it to dict). We send data to other threads using queue data
    type. The format is {'status_code' : 200/401/404 etc, 'response', server response}.
        Authorization only applied in Post, Update, and delete using 'auth_con' method. Please
    see 'set_security' method. The secret key is stored in 'conf/config.ini' and it will be 
    invoked by '_get_secret_key' method.
        Running this thread by invoking 'run' method.

    Attributes:
        queue_to_operation (Queue)  : Queue data intended to be sent to operation thread. 
                                      It contains dict type.
        queue_from_operation (Queue) : Queue data intended to be received by network thread.
        secret_key_local   (str)                 : Local secret key for auth local connections
        db_connection      (databaseConnector)   : Object for perfoming database transactions

    '''

    def __init__(self) -> None:
        self.queue_data = mp.Queue()
        SERVER_ADDRESS = self._read_config_file('server', 'address')
        self.secret_key = self._read_config_file('server', 'secret_key')
        self.db_connection = DatabaseConnector(SERVER_ADDRESS, endpoint_paths)
        self.lock = threading.Lock()


    def _read_queue_data(self) -> mp.Queue:
        '''
            Read shared data which is queue data type. No need lock method.
            queue is implementing safe-thread mechanism.

            Returns:
                queue data from thread operation
        '''
        return self.queue_data.get()


    def set_queue_data(self, queue_data: mp.Queue):
        '''
            This method set variable for shared queue data. 
        '''
        self.queue_data = queue_data


    def _read_config_file(self, section: str, param: str) -> str:
        '''
            This method helps to read configuration data in 'config.ini'.

            Args:
                section (str)     : The section in config file.
                param (str)       : The parameter in config file

            Returns:
                parsed_config_data (str)  : Parsed config data.

            Raises:
                configparser.Error: If there is an error reading the configuration file 
        '''
        parser_secret = configparser.ConfigParser()
        try:
            parser_secret.read(full_path_config_file)
            parsed_config_data = parser_secret.get(section, param)

        except configparser.NoOptionError as error_message:
            raise configparser.Error('Parameters not found in section')\
                from error_message
        except configparser.NoSectionError as error_message:
            raise configparser.Error('Section not found in configuration file') \
                from error_message
        except configparser.Error as error_message:
            raise configparser.Error(
                f'Error reading configuration file: {error_message}')

        return parsed_config_data

    def _parse_dict(self, data: dict) -> tuple:
        '''
            This method helps to parse data comming from other process
            to a tuple contains 'method' and 'payload'.

            Args:
                data   (dict)  : Data from other process

            Returns:
                method, payload (tuple) : Parsed data from 'method' and 'payload'

        '''
        method = data['method']
        payload = data['payload']
        return method, payload

    def _set_security(self, secret_key, algorithm, token_type, payload_header=None):
        '''
            This method helps to set security for auth. It uses 'encode' method 
            in database_connector driver lib.

            Args:
                secret_key   (str)  : Secret key for local connection
                algorithm    (str)  : Algorithm for encryption.
                token_type   (str)  : Token type for encryption. 
                payload_header(dict): Payload will be sent in header http.
                                      (default is {})
        '''
        if payload_header is None:
            payload_header = DEFAULT_PAYLOAD_HEADER

        self.db_connection.set_encode(secret_key, algorithm, token_type)
        self.db_connection.encode(payload_header)

    def _get_key_value(self, payload: dict) -> tuple:
        '''
            This method helps to get a pair of key-val dict and 
            convert it to tuple.

            Args:
                payload (dict)  : Data contains params eg. (id:10). It only used
                                  for get method and delete method (those use
                                  params in api, those don't use json)

            Returns:
                key, value (tuple)  : Params pair ([str]:[int]).

        '''
        key = list(payload.keys())[0]
        value = payload[key]
        return key, value

    def _auth_con(self):
        '''
            This method helps for authorize the connection between server. 
            By invoking this method, the connection will be encoded.

        '''
        self._set_security(
            secret_key=self.secret_key,
            algorithm='HS256',
            token_type='Bearer'
        )

    def _turn_off_auth(self):
        '''
            This method helps to turn off authorization in connection between server.                
        '''
        self.db_connection.reset_encode()

    def handle_commands(self, data: dict, auth_turn_on: bool = True) -> tuple:
        '''
            This method helps for performing database transactions with server.
            It will perform specific transaction base on 'method' variable (GET/DEL/ETC).

            Args:
                data (dict)         : Payload from operation thread.
                auth_turn_on (bool) : Authorization in connection. Default is ON !.

            Returns:
                http_code, 
                fin_resp (tuple[int][str]) : http code (int) and response from server (str) 

        '''
        http_code = None
        response = None

        # parsing data from other process
        method, payload = self._parse_dict(data)
        lowercase_method = str(method).lower()

        # set authorization option.
        # default is ON / True
        if auth_turn_on:
            self._auth_con()
        else:
            self._turn_off_auth()

        # check the method from other process payload
        if lowercase_method == "get":
            key, value = self._get_key_value(payload)
            http_code, response = self.db_connection.get_data(
                param=key, value=value)

        elif lowercase_method == "post":
            http_code, response = self.db_connection.post_data(
                payload, endpoint='post')

        elif lowercase_method == "delete":
            key, value = self._get_key_value(payload)
            http_code, response = self.db_connection.delete_data(
                param=key, value=value)

        elif lowercase_method == "update":
            http_code, response = self.db_connection.update_data(payload)

        elif lowercase_method == "success_items":
            http_code, response = self.db_connection.post_data(
                payload, endpoint='success_items')

        return http_code, response



class GetRequest (NetworkThread):
    def __init__(self) -> None:
        super().__init__()


    def set_queue_data_to_operation(self, queue_data):
        super().set_queue_data(queue_data)


    def run(self) -> None:
        '''
            Request GET method from server every 5 secs and put it on queue to operation.
            By performing this, we help operation thread focuses on the operation tasks
            only (let this thread only requests data to server). 

        '''
        oldest_response_text = None
        prev_time = time.time()
        while True:
            current_time = time.time()

            if current_time - prev_time >= NETWORK_TIMEOUT:
                prev_time = current_time
                responses = super().handle_commands(
                    PAYLOAD_GET_DATA, auth_turn_on=True)
                # only get the response text, index 0 is representing status code in interger
                # index 1 is representing the content/data from API.
                new_response_text = responses[1]
                '''
                    We have to store the latest data from server then compare them to
                    the newest data. If the newest data same as the oldest data, don't
                    send data to queue, else send it.
                
                '''
                if oldest_response_text != new_response_text: 
                    oldest_response_text = new_response_text   
                    self.queue_data.put(new_response_text)



class PostRequest (NetworkThread):
    '''
        Listening request method from operation thread by reading queue_data_from_operation.
        It sends method DELETE No_resi and POST No_resi + photos in success items  database in server. 
        By performing this, we help operation thread focuses on the operation 
        tasks only (let this thread requests data to server). 
    '''
    def __init__(self) -> None:
        super().__init__()

    def set_queue_data_from_operation(self, queue_data):
        super().set_queue_data(queue_data)

    def run(self) -> None:
        while True:
            queue_data_from_operation = super()._read_queue_data()
            if queue_data_from_operation is not None:
                payload = queue_data_from_operation
                responses = super().handle_commands(payload, auth_turn_on=True)
                response_text = responses[1]
                with self.lock:
                    log.logger.info("Response dari request : " +
                                str(response_text))
                
            


