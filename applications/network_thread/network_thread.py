"""
    File           : database_thread.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mar, 2023
    Description    : 

        This code handles network transaction between online server
    and device. It uses websocket protocol. No security applied
    in this version. 
        This code has 2 classes, class NetworkMethods is the class that handle 
    basic operation needed by class NetworkThread and class NetworkThread is 
    the class that run the behaviour of the thread.
    
    License: see 'licenses.txt' file in the root of project
"""

import json
import queue
import socket
import threading
import time
import logging

class NetworkMethods:
    '''
        Class NetworkMethods is the class that handle basic operation needed by 
    class NetworkThread. It uses socket library for connection to web server.
    There are 2 methods use lock library to access shared resources (read_queue_data 
    and send_queue_data). 
        This class performs connection to online webserver by socket protocol, read 
    queue data from another threads, send queue data to another thread, listening data 
    from webserver, and sending data to web server.

    Attributes:
        server_address (str)    : The online server address (arg).
        server_port (int)       : The port used in connection to webserver (arg).
        socket_obj              : Socket object from socket.socket class
        seocket.lock_obj        : Lock object from threading.lock() class

    NOTE: This only work for online webserver. Local server uses different method to connect.
          It uses socket.bint() method (see method conenct). In other hand, this class uses 
          socket.connect().
    
    '''
    def __init__(self, server_address: str, server_port: int) -> None:
        self._server_address = server_address
        self._server_port = server_port
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock_obj = threading.Lock()

    def connect(self, timeout: int)-> None:
        """
            This function helps to connect to webserver usisng websocket.

            Args:
                timeout (int) : timeout for connection to webserver(in secs)

            Returns:
                None
        """
        self.socket_obj.connect((self._server_address, self._server_port))
        self.socket_obj.settimeout(timeout)

    def recieve_data(self, payload_size: int)-> str:
        """
            This function helps to receive data from web server. It receives a byte-string data
            from server, so we need to decode it to string object.

            Args:
                payload_size (int) : the max size of payload from server (in byte).

            Returns:
                _decoded_data_received (str) : payload data from server in string object.
        """
        _data_received = self.socket_obj.recv(payload_size)
        _decoded_data_received = _data_received.decode('utf-8')
        return _decoded_data_received

    def send_data(self, data)->None:
        """
            This function helps to send data to web server. It needs to encode to byte-string
            data.

            Args:
                data (any) : data that intended to send.

            Returns:
                None
        """
        encoded_data = data.encode('utf-8')
        self.socket_obj.sendall(encoded_data)

    def read_queue_data(self, queue_data: queue.Queue):
        """
            This function helps to read data from shared resources queue. 
            It locks the resources when it reads the queue data (avoide
            race condition).
            
            Args:
                queue_data (queue.Queue) : Queue object from shared resources.

            Returns:
                _return (str) : Returns str 'empty' if queue is empty. 
                                Returns data if avaialable.
        """
        _return = ''
        with self.lock_obj:
            if queue_data.empty():
                _return = 'empty'
            else:
                _return = queue_data.get()
        return _return
    
    def send_queue_data(self, 
                        queue_data: queue.Queue, 
                        data: dict
                        ):
        """
            This function helps to send data to shared resources queue. 
            It locks the resources when it sends the queue data (avoide
            race condition). It returns 'queue is full' if queue is full,
            and returns 'success' if data is sent.
            
            Args:
                queue_data (queue.Queue) : Queue object from shared resources.
                data    (dict)           : Data to be send. Suggested in JSON fromat.

            Returns:
                status (str)   : Status of opeartion.
        """
        with self.lock_obj:
            try:
                queue_data.put(data, block=False)
            except queue.Full:
                return 'queue is full'
            return 'success'
    
    def get_sock_opt(self):
        """
            This function helps to check socket connection. It uses socketgetop methods
            from socket class.
            Args:
                None
            Returns:
                status (str) : socket status.s
        """
        _return_code = self.socket_obj.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        return "socket not active" if _return_code != 0 else "socket active"

    def _parse_data_from_json(self, data):
        """
            This private function helps to parse JSON data from server to python dict object.
            
            Args:
                data (JSON)        : JSON data received from server.

            Returns:
                _parsed_data (str) : Parsed data to dict objects
        """
        _parsed_data = json.loads(data)
        return _parsed_data

    def _encode_data_to_json(self, data):
        """
            This private function helps to encode dict object to JSON format.
            
            Args:
                data (JSON)        : JSON data received from server.

            Returns:
                _parsed_data (str) : Encoded JSON format.
        """
        _encoded_data = json.dumps(data)
        return _encoded_data


TIMEOUT = 5  # timeout connecting to server (secs)
DELAY_RECONNECT = 5
PAYLOAD_SIZE = 1024

logger = logging.getLogger(__name__)

class NetworkThread:
    '''
        This class is the treading of network_thread. It will connecting until it connects
        , check the socket's alive, listen data from web server, send data to storage-thread 
        queue if data received, read data from  opeartion-thread queue.

        Attributes:
            server_address (str)            : The online server address (arg).
            server_port (int)               : The port used in connection to webserver (arg).
            queue_data_from_thread (queue)  : Queue object from another thread. It will read.
            queue_to_send (queue)           : Queue object to sending data.

    '''
    def __init__(self, server_address: str, 
                 server_port: int, 
                 queue_to_read:queue.Queue, 
                 queue_to_send: queue.Queue
                 ) -> None:
        self._net_methods = NetworkMethods(server_address, server_port)
        self._not_connected = True  # initial connection is always disconnect
        self._queue_data_from_the_thread = queue_to_read
        self._queue_for_other = queue_to_send

    def run(self)->None:
        """
            This function run the thread of network thread.
            
            Args:
                None

            Returns:
                None
        """
        while True:
            # connect to online server
            if self._not_connected:
                self._connect_to_server(timeout_server=TIMEOUT)
            try:
                received_data_server = self._net_methods.recieve_data(PAYLOAD_SIZE)
            except socket.error as msg_err:
                logger.error(f"Error receiving data from server: {msg_err}")
                time.sleep(DELAY_RECONNECT)
                continue
            # check if socket is still active
            socket_status = self._net_methods.get_sock_opt()
            if socket_status == 'socket not active':
                logger.error('socket is not active!')
                self._not_connected = True
            # listen data from online server
            if received_data_server:
                parsed_data = self._net_methods._parse_data_from_json(received_data_server)
                 # send data to another queue data (Mutex)
                result_opt = self._net_methods.send_queue_data(self._queue_for_other, parsed_data)
                if result_opt == "queue is full":
                    logger.warning("Queue is full")
            try:
                # read data from another queue data (Mutex)
                data_to_read = self._net_methods.read_queue_data(self._queue_data_from_the_thread)
                if data_to_read != "empty":
                    encoded_data_to_json = self._net_methods._encode_data_to_json(data_to_read)
                    self._net_methods.send_data(encoded_data_to_json)
            except socket.error as error_msg:
                logger.error(f"Error sending data to server: {error_msg}")
                continue
      
    def _connect_to_server(self, timeout_server)->None:
        """
            This private function helps to handle connection to server.
            
            Args:
                timeout_server     : timeout connection to server (in secs)

            Returns:
                None
        """
        while True:
            try:
                self._net_methods.connect(timeout=timeout_server)
                logger.info("Connected successfully")
                self._not_connected = False
                break
            except socket.error as error_msg:
                logger.error(f"Error connecting to server: {error_msg}")
                time.sleep(DELAY_RECONNECT)
