"""
    File           : network.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

        This code handles requests to API Server. 
    
    License: see 'licenses.txt' file in the root of project
"""
import configparser
import os
import sys
import threading
import multiprocessing as mp
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/database_connector'))
sys.path.append(os.path.join(parent_dir, 'utils'))

import log
from database_connector import DatabaseConnector

full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')

# Endpoints url of API
endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php', 'success_items' : 'success_items.php'}

# We don't send data in http header, so keep it empty.
# It exists only for content of auth requests.
DEFAULT_PAYLOAD_HEADER = {} 
PAYLOAD_GET_DATA = {'method': 'GET', 'payload': {'no_resi': '0'}}

class NetworkThread:
    '''
        Class Storagethread is the class that handle local storage operation. It receives
    data from thread operation and thread network. It uses mysql DBMS and XAMPP. Server
    is written by PHP native.
          It uses database_connector driver lib to perform database transaction. Queue data
    contain payload as dictionary will be parse as 'method' [post, update, delete, get] and
    'payload' contains dictionary data. Method will be used as parameter to perform specific
    transacation from local server. It will return status_code and response from local server
    as tuple type (then we convert it to dict). We send data to other threads using queue data
    type. The format is {'status_code' : 200/401/404 etc, 'response', server response}.
        Authorization only applied in Post, Update, and delete using 'auth_con' method. Please
    see 'set_security' method. The secret key is stored in another dir and it will be invoked
    by '_get_secret_key' method.
        Running this thread by invoking 'run' method.

    Attributes:
        secret_key_local      (str)                 : Local secret key for auth local connections
        db_connection         (databaseConnector)   : Object for perfoming database transactions

    '''
    def __init__(self) -> None:
        self.queue_to_operation = mp.Queue()
        self.queue_from_operation = mp.Queue()
        SERVER_ADDRESS = self._read_config_file('server', 'address')
        self.secret_key= self._read_config_file('server', 'secret_key')
        self.db_connection = DatabaseConnector(SERVER_ADDRESS, endpoint_paths)

        self.lock = threading.Lock()
    

    def _read_queue_from_operation(self)->mp.Queue:
        with self.lock:
            return None if self.queue_from_operation.empty() \
                else self.queue_from_operation.get(timeout=1)
        


    def set_queue_to_operation(self, queue_to_operation: mp.Queue):
        self.queue_to_operation = queue_to_operation


    def set_queue_from_operation(self, queue_from_operation:mp.Queue):
        self.queue_to_operation = queue_from_operation


    def _read_config_file(self, section:str, param:str) -> str:
        """
        This function helps to read configuration data in 'config.ini'.

        Args:
            section (str)     : The section in config file.
            param (str)       : The parameter in config file

        Returns:
            parsed_config_data (str)  : Parsed config data.

        Raises:
            configparser.Error: If there is an error reading the configuration file 
        """
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
            raise configparser.Error(f'Error reading configuration file: {error_message}')

        return parsed_config_data


    def _parse_dict(self, data:dict)->tuple:
        """
            This function helps to parse data comming from other process
            to a tuple contains 'method' and 'payload'.
            
            Args:
                data   (dict)  : Data from other process

            Returns:
                method, payload (tuple) : Parsed data from 'method' and 'payload'
                
        """
        method      = data['method']
        payload     = data['payload']
        return method, payload


    def _set_security(self, secret_key, algorithm, token_type, payload_header = None):
        """
            This function helps to set security for auth. It uses 'encode' method 
            in database_connector driver lib.
            
            Args:
                secret_key   (str)  : Secret key for local connection
                algorithm    (str)  : Algorithm for encryption.
                token_type   (str)  : Token type for encryption. 
                payload_header(dict): Payload will be sent in header http.
                                      (default is {})

        """
        if payload_header is None:
            payload_header = DEFAULT_PAYLOAD_HEADER

        self.db_connection.set_encode(secret_key, algorithm, token_type)
        self.db_connection.encode(payload_header)


    def _get_key_value(self, payload: dict) -> tuple:
        """
            This function helps to get a pair of key-val dict and 
            convert it to tuple.
            
            Args:
                payload   : Data contains params eg. (id:10). It only used
                            for get method and delete method (those use
                            params in api, those don't use json)

            Returns:
                key, value (tuple)  : Params pair ('id':25).
                
        """
        key = list(payload.keys())[0]
        value = payload[key]
        return key, value


    def _auth_con(self):
        """
            This function helps to auth the connection to server.
            By invoking this function, the connection will be encoded.
                
        """
        self._set_security(
            secret_key = self.secret_key,
            algorithm='HS256',
            token_type='Bearer'
        )


    def _turn_off_auth(self):
        """
            This function helps to turn off auth in connection to server.                
        """
        self.db_connection.reset_encode()

    

    def handle_commands(self, data:dict, auth_turn_on:bool = True)->tuple:
        """
            This function helps to performing database transaction to server.
            It will perform specific transaction base on 'method' variable.
            
            Args:
                data (dict)         : Payload from incoming another queue data thread.
                auth_turn_on (bool) : Put authorization in connection. Default is On.

            Returns:
                http_code, 
                fin_resp (tuple) : http code and response from local server 
                                   
        """
        http_code = None
        response = None
        
        #parsing data from other process
        method, payload = self._parse_dict(data) 
        lowercase_method = str(method).lower()

        # set authorization option 
        # default is True
        if auth_turn_on:
            self._auth_con()
        else:
            self._turn_off_auth()

        # check the method from other process payload
        if lowercase_method == "get":
            key, value = self._get_key_value(payload)
            http_code, response = self.db_connection.get_data(param=key, value=value)

        elif lowercase_method == "post":
            http_code, response = self.db_connection.post_data(payload, endpoint='post')

        elif lowercase_method == "delete":
            key, value = self._get_key_value(payload)
            http_code, response = self.db_connection.delete_data(param=key, value=value)

        elif lowercase_method == "update":
            http_code, response = self.db_connection.update_data(payload)

        elif lowercase_method == "success_items":
            http_code, response = self.db_connection.post_data(payload, endpoint='success_items')

        return http_code, response 
    

    def run(self) -> None:
        prev_time = time.time()
        while True:
            current_time = time.time()
            if current_time - prev_time >= 5:
                prev_time = current_time
                status, response = self.handle_commands(PAYLOAD_GET_DATA, auth_turn_on=True)
                # send data to queue_to_operation
                with self.lock:
                    self.queue_to_operation.put(response, timeout = 1)

            queue_data_from_operation = self._read_queue_from_operation()
            if queue_data_from_operation != None:
                payload = queue_data_from_operation
                status, response = self.handle_commands(payload, auth_turn_on=True)
                log.logger.info("Response dari request : " + str(response))
                
            


