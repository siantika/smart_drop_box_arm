import json
import queue
import sys
sys.path.append('drivers/database_connector')
from database_connector import DatabaseConnector

TEST_SECRET_KEY_LOCAL = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

LOCALHOST_ADDR = 'http://127.0.0.1'
test_endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php'}

AUTH_HEADER = {}

class StorageThread:
    def __init__(self) -> None:
        self.queue_from_thread_opt = ""
        self.queue_to_thread_opt = ""
        self.queue_from_thread_net = ""
        self.db = DatabaseConnector(LOCALHOST_ADDR, test_endpoint_paths)

    def set_queue(self,
                  queue_from_thread_opt:queue.Queue,
                  queue_to_thread_opt:queue.Queue,
                  queue_from_thread_net:queue.Queue
                  )-> None:
        self.queue_from_thread_opt = queue_from_thread_opt
        self.queue_to_thread_opt   = queue_to_thread_opt
        self.queue_from_thread_net = queue_from_thread_net

    def decode_json_to_dict(self, data)-> dict:
        decoded_data = json.loads(data)
        return decoded_data
    
    def parse_dict(self, data:dict)->tuple:
        method      = data['method']
        del data['method']
        keys        = data.keys()
        listed_keys = list(keys)
        payload     =  dict((key, data[key]) for key in listed_keys)
        return method, payload

    def set_security(self, secret_key, algorithm, token_type, payload_header=AUTH_HEADER):
        self.db.set_encode(secret_key, algorithm, token_type)
        self.db.encode(payload_header)
        
    def send_request(self, data:dict):
        ret_data  = self.parse_dict(data)
        method    = ret_data[0]
        payload   = ret_data[1]

        if method == "GET":
            self.db.reset_encode() 
            key = list(payload.keys())[0]  # get the first (and only) key in the dictionary
            value = int(payload[key])  
            http_code, response = self.db.get_data(param=key, value=value)
            decoded_resp = self.decode_json_to_dict(response)
            fin_resp = decoded_resp
        elif method == "POST":
            self.set_security(
                secret_key= TEST_SECRET_KEY_LOCAL,
                algorithm = 'HS256',
                token_type= 'Bearer'
            )
            http_code, response = self.db.post_data(payload)
            fin_resp = response
        elif method == "DELETE":
            key = list(payload.keys())[0]  # get the first (and only) key in the dictionary
            value = int(payload[key])  
            self.set_security(
                secret_key= TEST_SECRET_KEY_LOCAL,
                algorithm = 'HS256',
                token_type= 'Bearer'
            )
            http_code, response = self.db.delete_data(param=key, value=value)
            fin_resp = response
        elif method == "UPDATE":
                self.set_security(
                secret_key= TEST_SECRET_KEY_LOCAL,
                algorithm = 'HS256',
                token_type= 'Bearer'
            )
                http_code, response = self.db.update_data(payload)
                fin_resp = response

        return http_code, fin_resp

