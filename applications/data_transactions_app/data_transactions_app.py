'''
    File           : data transactions app
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : July, 2023
    Description    : 

    This file is intended for creating data transactions thread.
    Data transactions in smart drop box app are controlled by
    2 apps:
        1. Get no_resi routine : get full data  based on no resi param
           every 5 secs
        2. Send request : process data base on other thread requests.
    
    This app designed with run method for invoking the infinite main code
    of apps. It uses 'Queue (multiprocessing.Queue) for payload transaction between
    threads. It already implement safety-thread mechanism'

    To create a thread, you need to create a function that invokes app.run()
    and pass the shared queue as args. Please see multiprocessing lib API docs for
    further informations (on internet).
    
'''
import os
from pathlib import Path
import sys
import multiprocessing as mp
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/data_access'))
sys.path.append(os.path.join(parent_dir, 'utils'))
full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')

# Should put this imports below appending paths.
# To recognize the libraries.
from data_access import HttpDataAccess
from Interfaces import AppInterface
import log
import configparser

# Constant 
TIMEOUT_REQUEST = 10 # secs

# Utility functions
def read_config_file(config_file_path: Path, section: str, param: str) -> str:
    '''
    Reads configuration file in 'config.ini'.
    Args:
        section (str): The section in the config file.
        param (str): The parameter in the config file
    Returns:
        value of intended param.
    Raises:
        configparser.Error: If there is an error reading the 
                                configuration file 
    '''
    parser_secret = configparser.ConfigParser()
    try:
        parser_secret.read(config_file_path)
        parsed_config_data = parser_secret.get(section, param)
    except Exception as error:
        raise configparser.Error(f'Error reading configuration file: {error}')
    return parsed_config_data

"""         Interface for data transactions          """


"""                 Private Classess                 """
class EndpointProcessor:
    """
    Class for processing HTTP requests based on provided payload and endpoint metadata.

    Args:
        endpoint_metadata (dict[str, list[str]]): A dictionary mapping endpoint keys 
        to lists of file names. request_processor (HttpDataAccess): An instance 
        of the HttpDataAccess class that provides HTTP request methods.
    """

    def __init__(self, endpoint_metadata: dict[str, list[str]], request_processor: HttpDataAccess) -> None:
        self._endpoint_metadata = endpoint_metadata
        self._request_processor = request_processor

    def _find_http_method(self, payload: dict) -> str | None:
        """
        Find the associated HTTP method for the given payload.

        Args:
            payload (dict): The payload containing the 'endpoint' key.

        Returns:
            str | None: The HTTP method associated with the endpoint, or None if not found.
        """
        endpoint = payload['endpoint']
        for endpoint_key, file_names in self._endpoint_metadata.items():
            if endpoint in file_names:
                return endpoint_key
        return None

    def _find_endpoint(self, payload: dict) -> str:
        """
        Find the endpoint name from the given payload.

        Args:
            payload (dict): The payload containing the 'endpoint' key.

        Returns:
            str: The name of the endpoint.
        """
        return payload['endpoint']

    def _find_http_data(self, payload: dict) -> dict:
        """
        Find the HTTP data from the given payload.

        Args:
            payload (dict): The payload containing the 'data' key.

        Returns:
            dict: The HTTP data from the payload.
        """
        return payload['data']

    def _find_http_header(self, payload: dict) -> dict:
        """
        Find the HTTP header from the given payload.

        Args:
            payload (dict): The payload containing the 'http_header' key.

        Returns:
            dict: The HTTP header from the payload.
        """
        return payload['http_header']

    def _http_method_mapping(self) -> dict:
        """
        Return a mapping of HTTP methods to their corresponding processor methods.

        Returns:
            dict: A mapping of HTTP methods to processor methods.
        """
        return {
            'get': self._request_processor.get,
            'post': self._request_processor.post,
            'update': self._request_processor.update,
            'delete': self._request_processor.delete,
        }

    def _http_request_processor(self, http_method_function, http_data,
                                endpoint, http_header) -> tuple[int, any]:
        """
        Process the HTTP request using the appropriate method.

        Args:
            http_method_function: The HTTP method function to be used for processing the request.
            http_data (dict): The HTTP data to be processed.
            endpoint (str): The endpoint name.
            http_header (dict): The HTTP header to be used in the request.

        Returns:
            http status code and response from server.
            (tuple[int,any])

        Raises:
            ValueError: If the endpoint is not found or not registered.
            RuntimeError: If an error occurs while processing the HTTP request.
        """
        try:
            return http_method_function(
                param=http_data,
                endpoint=endpoint,
                http_header=http_header,
                timeout=TIMEOUT_REQUEST
            )
        except TypeError:
            raise ValueError("Endpoint not found or not registered!")
        except Exception as error:
            raise RuntimeError(f"Error processing HTTP request: {str(error)}")

    def process(self, payload: dict) -> tuple[int, str]:
        """
        Process the HTTP request based on the provided payload and return 
        a tuple with the status code and response.

        Args:
            payload (dict): The payload containing the necessary information 
            for processing the request.

        Returns:
            tuple[int, str]: A tuple containing the status code and response.
        """
        http_method = self._find_http_method(payload)
        http_data = self._find_http_data(payload)
        http_header = self._find_http_header(payload)
        endpoint = self._find_endpoint(payload)

        # Get the appropriate HTTP method function from the mapping
        http_methods_mapping = self._http_method_mapping()
        http_method_function = http_methods_mapping.get(http_method)

        return self._http_request_processor(http_method_function, http_data, endpoint, http_header)


"""             Nertwork App Class and its childs class           """
# Constants
TIME_INTERVAL_GET_REQUEST = 5   # In secs
# payload fot getting all not finished no resi in server
PAYLOAD_GET_DATA = {
    "endpoint": "get.php",
    "data": {},
    "http_header": {"content-type": "application/json"}
}

# Endpoint and it's method. It matches main app requirements
# Open for extention if new endpoints or methods are registered
ENDPOINT_META_DATA = {
        'get': ['get.php'],
        'post': ['success_item.php', 'post.php'],
        'update': ['update.php'],
        'delete': ['delete.php'],
    }


class HttpGetResiDataRoutineApp(AppInterface):
    """ Performs sending a request 'get' every TIME_INTERVAL_GET_REQUEST. 
        We supplied the default payload since we need access all the stored
        data in  server (read API doc for more clarity). It only send the new
        data. If data are not changed in server, it will not send the old data.
        NOTE: This code implements infinite loop for multithreading purpose.
    """

    def __init__(self) -> None:
        server_address = read_config_file(full_path_config_file,
                                          'server', 'address')
        self._data_access_proccessor = HttpDataAccess(server_address)
        self._data_processor = EndpointProcessor(ENDPOINT_META_DATA, 
                                                 self._data_access_proccessor)
        self._shared_queue_data = mp.Queue()
        self._old_response_text = None

    def set_queue_data(self, queue_data: mp.Queue):
        """ Set a shared queue for sending  'get' response from server """
        self._shared_queue_data = queue_data

    def _process_requests(self, response_text:dict)->dict[str:dict]:
        """ Process requests text and returns it as key-val data. 
            Key is 'no resi' and value is dictionary contains data payload
            from server (inlcuding no resi). It eases us for finding data in
            controller app
        """
        data_items = response_text[1]
        key_val_data = {data_item['no_resi']: data_item for data_item in data_items}
        return key_val_data

    def _get_request_routine(self):
        responses = self._data_processor.process(PAYLOAD_GET_DATA)
        # Only get the response text, index 0 represents http status code
        # and index 1 represents the content/data from the API.
        new_response_text = self._process_requests(responses)
        # Just put the newest data from server. Prevents unecessary
        # put data to queue
        if self._old_response_text != new_response_text:
            self._old_response_text = new_response_text
            self._shared_queue_data.put(new_response_text)

    def run(self) -> None:
        """ 
            Executes infinite get-request-routine app.
            Performs periodic get requests to server base on
            given interval time in seconds. 
            Example data to be sent through queue:
            {
                '5555' : {
                'no_resi' : '5555',
                'item' : 'sandal',
                'date_ordered' : '25/02/2024'
                },
                etc ...
            }
        """
        prev_time = time.time()
        while True:
            current_time = time.time()
            if current_time - prev_time >= TIME_INTERVAL_GET_REQUEST:
                prev_time = current_time
                self._get_request_routine()


class HttpSendDataApp(AppInterface):
    '''
        Performs reading data from other thread using queue then it will
        send received data (request to the server) to specific endpoint 
        according  payload processed. It logs the success operations
        (see log 'module' in /utils dir).
    '''

    def __init__(self) -> None:
        server_address = read_config_file(full_path_config_file,
                                          'server', 'address')
        self._data_access_processor = HttpDataAccess(server_address)
        self._data_processor = EndpointProcessor(ENDPOINT_META_DATA,
                                                 self._data_access_processor)
        self._shared_queue_data = mp.Queue()

    def set_queue_data(self, queue_data: mp.Queue):
        """ Set a shared queue for reading  requests from other threads.
            It sends the requests to the server.
         """
        self._shared_queue_data = queue_data

    def _read_data_from_queue(self) -> mp.Queue:
        """ Read incoming data from other thread using queue.
            Block process if no data comming.            
        """
        return self._shared_queue_data.get()

    def _send_request_app(self) -> None:
        payload = self._read_data_from_queue()
        if payload is not None:
            # Only get the response text, index 0 represents http status code
            # and index 1 represents the content/data from the API.
            responses = self._data_processor.process(payload)
            response_text = responses[1]
            # Already implements safety-thread
            log.logger.info(f"Response dari request : {response_text}")

    def run(self) -> None:
        """ Executes infinite send-requests app"""
        while True:
            self._send_request_app()
