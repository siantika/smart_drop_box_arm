"""
    File           : storage_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

        This code handles local storage proccess. It handles data from thread operation
    and from thread network (queue data from threads). It receives payload in dict data 
    type {'method' : get/post/etc, 'params' : params} from those threads. It will send 
    responses to two ohters thread( queue data to threads) as dict data {'status_code':
    200/404/etc, 'response' : local server response}
    
    License: see 'licenses.txt' file in the root of project
"""
import configparser
import json
import queue
import threading
import sys
sys.path.append('drivers/database_connector')
from database_connector import DatabaseConnector


LOCALHOST_ADDR = 'http://127.0.0.1/smart_drop_box/'
endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php'}

DEFAULT_PAYLOAD_HEADER = {} # we don't send data in header http, so keep it empty.

class StorageThread:
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
        queue_from_thread_opt (queue.Queue)         :Queue data from thread opeartion
                                                     intended to be read by storage thread 
        queue_to_thread_opt   (queue.Queue)         :Queue data to thread opeartion
                                                     intended to be sent by storage thread 
        queue_from_thread_net (queue.Queue)         :Queue data from thread opeartion
                                                     intended to be read by storage thread 
        queue_to_thread_net   (queue.Queue)         :Queue data to thread network thread
                                                     intended to be sent by storage thread 
        secret_key_local      (str)                 : Local secret key for auth local connections
        db_connection         (databaseConnector)   : Object for perfoming database transactions
        lock                  (threading)           : Object for perfom lock (mutex)

    NOTE: All queue data should be in DICTIONARY type.

    '''
    def __init__(self) -> None:
        self.queue_from_thread_opt = ""
        self.queue_to_thread_opt   = ""
        self.queue_from_thread_net = ""
        self.queue_to_thread_net   = ""
        self.secret_key_local      = self._get_secret()
        self.db_connection = DatabaseConnector(LOCALHOST_ADDR, endpoint_paths)
        self.lock = threading.Lock()

    def _get_secret(self) -> str:
        """
        This function helps to get secret key from another dir.

        Returns:
            secret_key (str)  : secret key for auth local connection.

        Raises:
            configparser.Error: If there is an error reading the configuration file or
                                the secret key is not found.
        """
        parser_secret = configparser.ConfigParser()
        try:
            parser_secret.read('./conf/config.ini')
            secret_key = parser_secret.get('secret', 'local_server_secret_key')
        except configparser.NoOptionError as error_message:
            raise configparser.Error('local_server_secret_key not found in secret section')\
                  from error_message
        except configparser.NoSectionError as error_message:
            raise configparser.Error('Secret section not found in configuration file') \
                from error_message
        except configparser.Error as error_message:
            raise configparser.Error(f'Error reading configuration file: {error_message}')

        return secret_key


    def set_queue(self,
                  queue_from_thread_opt:queue.Queue,
                  queue_to_thread_opt:queue.Queue,
                  queue_from_thread_net:queue.Queue,
                  queue_to_thread_net : queue.Queue,
                  )-> None:
        """
            This function helps to set queue data threads. the queue data
            will be used in data communication between threads.
            
            Args:
                   queue_from_thread_opt (queue.Queue) 
                   queue_to_thread_opt   (queue.Queue)
                   queue_from_thread_net (queue.Queue)
                   queue_to_thread_net   (queue.Queue) 

            Returns:
                None
                
        """
        self.queue_from_thread_opt = queue_from_thread_opt
        self.queue_to_thread_opt   = queue_to_thread_opt
        self.queue_from_thread_net = queue_from_thread_net
        self.queue_to_thread_net   = queue_to_thread_net

    def decode_json_to_dict(self, data)-> dict:
        """
            This function helps to decode json file from other threads
            to dict type.
            
            Args:
                data (dict)  : Data from other threads.

            Returns:
                decoded_data (dict) : decoded data to dict type
                
        """
        decoded_data = json.loads(data)
        return decoded_data

    def parse_dict(self, data:dict)->tuple:
        """
            This function helps to parse data comming from other threads
            to a list contains method and payload.
            
            Args:
                data   (dict)  : Data from other threads.

            Returns:
                method, payload (tuple) : Parsed data
                
        """
        method      = data['method']
        del data['method']
        keys        = data.keys()
        listed_keys = list(keys)
        payload     =  dict((key, data[key]) for key in listed_keys)
        return method, payload

    def set_security(self, secret_key, algorithm, token_type, payload_header = None):
        """
            This function helps to set security for auth. It uses 'encode' method 
            in database_connector driver lib.
            
            Args:
                secret_key   (str)  : Secret key for local connection
                algorithm    (str)  : Algorithm for encryption.
                token_type   (str)  : Token type for encryption. 
                payload_header(dict): Payload will be sent in header http.
                                      (default is {})

            Returns:
                None
                
        """
        if payload_header is None:
            payload_header = DEFAULT_PAYLOAD_HEADER#

        self.db_connection.set_encode(secret_key, algorithm, token_type)
        self.db_connection.encode(payload_header)

    def _get_key_value(self, payload: dict) -> tuple:
        """
            This function helps to get a pair of key-val dict and 
            convert it to tuple.
            
            Args:
                payload   : Data contains params eg. (id:10). It uses
                            for get method and delete method (those use
                            params in api, those don't use json)

            Returns:
                key, value (tuple)  : Params pair ('id':25).
                
        """
        key = list(payload.keys())[0]
        value = int(payload[key])
        return key, value

    def auth_con(self):
        """
            This function helps to auth the connection to local server.
            By invoking this function, the connection will be encoded.
            
            Args:
                None

            Returns:
                None
                
        """
        self.set_security(
            secret_key = self.secret_key_local,
            algorithm='HS256',
            token_type='Bearer'
        )

    def handle_commands(self, data: dict)->tuple:
        """
            This function helps to performing database transaction to local server.
            It will perform specific transaction base on 'method' variable
            
            Args:
                data (dict)      : Payload from incoming another queue data thread.

            Returns:
                http_code, 
                fin_resp (tuple) : http code and response from local server 
                                   
        """
        http_code = None
        fin_resp = None
        method, payload = self.parse_dict(data)
        lowercase_method = str(method).lower()
        if lowercase_method == "get":
            key, value = self._get_key_value(payload)
            self.db_connection.reset_encode()
            http_code, response = self.db_connection.get_data(param=key, value=value)
            fin_resp = self.decode_json_to_dict(response)
        elif lowercase_method in ("post", "delete", "update"):
            self.auth_con()
            if lowercase_method == "post":
                http_code, fin_resp = self.db_connection.post_data(payload)
            elif lowercase_method == "delete":
                key, value = self._get_key_value(payload)
                http_code, fin_resp = self.db_connection.delete_data(param=key, value=value)
            elif lowercase_method == "update":
                http_code, fin_resp = self.db_connection.update_data(payload)
        return http_code, fin_resp
    def send_queue_data(self, data:dict, queue_data: queue.Queue)-> str:
        """
            This function helps to send data to shared resources queue. 
            It locks the resources when it reads the queue data (avoid
            race condition).
            
            Args:
                data       (dict)        : Data to be sent.
                queue_data (queue.Queue) : Queue object from shared resources.

            Returns:
                _return (str) : Returns str 'empty' if queue is empty. 
                                Returns success if avaialable.
        """
        with self.lock:
            try:
                queue_data.put(data, block=False)
            except queue.Full:
                return 'queue is full'
            return 'success'

    def read_queue_data(self, queue_data: queue.Queue)-> None:
        """
            This function helps to read data from shared resources queue. 
            It locks the resources when it reads the queue data (avoid
            race condition).
            
            Args:
                queue_data (queue.Queue) : Queue object from shared resources.

            Returns:
                _return (str) : Returns str 'empty' if queue is empty. 
                                Returns data if avaialable.
        """
        with self.lock:
            return 'empty' if queue_data.empty() else \
                  queue_data.get()

    def _convert_to_dict(self, data:tuple)-> dict:
        """
            This function helps to converting tuple type to dict
            
            Args:
                data (tuple)     : Data in tuple-data-type to be converted.

            Returns:
                data_dict (dict) : Data in dict type with 2 key-value format 
                                   (sending format). 
        """
        status_code = data[0]
        response    = data[1]
        data_dict   = {
                       'status_code' : status_code,
                       'response'    : response
                    }
        return data_dict

    def run(self)-> None:
        '''
            This function is the excution of the storage thread.
                
            Args:
                None

            Returns:
                None

        '''
        queue_from_server  = self.read_queue_data(self.queue_from_thread_net)
        queue_from_thd_opt = self.read_queue_data(self.queue_from_thread_opt)

        if queue_from_server != 'empty':
            ret       = self.handle_commands(queue_from_server)
            payload   = ret
            self.send_queue_data(payload, self.queue_to_thread_net)
        if queue_from_thd_opt  != 'empty':
            ret       = self.handle_commands(queue_from_thd_opt)
            payload   = ret
            self.send_queue_data(payload, self.queue_to_thread_opt)
