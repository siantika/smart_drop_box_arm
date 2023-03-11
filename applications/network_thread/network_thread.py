import json
import queue
import socket

class NetworkMethods:
    def __init__(self, server_address:str, server_port:int) -> None:
        self._server_address = server_address
        self._server_port = server_port
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, timeout:int):
        self.socket_obj.connect((self._server_address, self._server_port))
        self.socket_obj.settimeout(timeout)

    def recieve_data(self, payload_size:int):
        _data_received = self.socket_obj.recv(payload_size)
        _decoded_data_received = _data_received.decode('utf-8')
        return _decoded_data_received
    
    def read_queue_data(self,queue_data:queue.Queue):
        return queue_data

    def send_queue_data(self, queue_data_to_be_sent: queue.Queue, data_to_send:dict):
        queue_data_to_be_sent.put(data_to_send)

    def _parse_data_from_json(self, data):
        _parsed_data = json.loads(data)
        return _parsed_data
    
    def _encode_data_to_json(self, data):
        _encoded_data = json.dumps(data)
        return _encoded_data


        
        

    


