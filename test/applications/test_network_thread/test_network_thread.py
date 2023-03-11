'''
    1. Listening data from server
    2. if new data arrived, check the security
    3. Then, sends it to storage queue.
    4. if thread_queue is got new data, send it to server.

'''

from unittest.mock import patch
import socket
import queue
import json
import sys
sys.path.append('applications/network_thread')
from network_thread import NetworkMethods

class TestNetworkMethodsInit:
    def help_mock_socket_method(self):
        self.mock_socket_socket = patch('socket.socket').start()

    def stop_all_patch(self):
        patch.stopall()

    def test_init_method_should_has_correct_attributes(self):
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)

        assert hasattr(net_t, '_server_address')
        assert hasattr(net_t, '_server_port')
        assert hasattr(net_t, 'socket_obj')

    def test_init_attributes_should_has_correct_initial_value_and_data_type(self):
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)

        assert net_t._server_address == '127.0.0.1'
        assert net_t._server_port == 5000


    def test_init_method_should_create_object_socket_tcp(self):
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)

        assert isinstance(net_t.socket_obj, socket.socket)

    def test_init_method_should_invoke_socket_socket_method_with_correct_args(self):
        self.help_mock_socket_method()

        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)

        self.mock_socket_socket.assert_called_once_with(
            socket.AF_INET, socket.SOCK_STREAM)
        self.stop_all_patch()


class TestNetworkConnect:
    def help_mock_method_connect(self):
        self.mock_connect = patch('socket.socket.connect').start()
        self.mock_set_time_out = patch ('socket.socket.settimeout').start()
        self.mock_connect.return_value = None

    def stop_all_patch(self):
        patch.stopall()

    def test_connect_method_should_called_correctly(self):
        self.help_mock_method_connect()
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)

        net_t.connect(timeout = 5)

        self.mock_connect.assert_called_once_with(('127.0.0.1', 5000))
        self.mock_set_time_out.assert_called_once_with(5)


class TestNetworkReceive:
    def help_mock_socket_method(self):
        self.mock_recv = patch('socket.socket.recv').start()

    def stop_all_patch(self):
        patch.stopall()

    def test_receive_data_method_should_invoke_correctly(self):
        self.help_mock_socket_method()
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)
        net_t.recieve_data(payload_size=1024)

        self.mock_recv.assert_called_once_with(1024)
        self.stop_all_patch()

    def test_receive_data_method_should_return_received_data(self):
        self.help_mock_socket_method()
        self.mock_recv.return_value = b'{"id":"2", "name":"solder", "no_resi":"2356"}'
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)
        _ret_val = net_t.recieve_data(payload_size=1024)

        assert _ret_val == '{"id":"2", "name":"solder", "no_resi":"2356"}'
        self.stop_all_patch()



class TestQueueData:
    def help_mock_queue_methods(self):
        self.mock_queue_put = patch('queue.Queue.put').start()
    
    def stop_all_patch(self):
        patch.stopall()

    def test_read_queue_data_should_be_invoked_correctly(self):
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)
        q = queue.Queue()
        _ret_val = net_t.read_queue_data(q)

        assert isinstance(_ret_val, queue.Queue)

    def test_send_queue_data_should_be_invoked_correctly(self):
        self.help_mock_queue_methods()
        self.mock_queue_put.return_value = None
        net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)
        q = queue.Queue()
        test_data = {
            "method":"POST",
            "id" : "8",
            "name" : "arduino uno",
            "no_resi" : "8595",
            "date_created" : "2023-03-04 20:43:55",
        }

        net_t.send_queue_data(q,test_data)

        self.mock_queue_put.assert_called_once_with(test_data)

        self.stop_all_patch()


class TestParsingDataMethod:
    '''
        NOTE: there is no JSON type, it only format. In python, it just dict/list type!
    '''
    def test_parse_data_from_server_as_json_format(self):
        # prepare test data (no json format)
        test_json_data = {
            "method": "POST",
            "id": "8",
            "name": "arduino uno",
            "no_resi": "8595",
            "date_created": "2023-03-04 20:43:55",
        }

        with patch('json.loads') as mock_loads:
            mock_loads.return_value = json.dumps(test_json_data)
            net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)
            _ret_val = net_t._parse_data_from_json(json.dumps(test_json_data))

            mock_loads.assert_called_once_with(json.dumps(test_json_data))
            assert _ret_val == json.dumps(test_json_data)


    def test_ecode_data_to_json_format(self):
        # prepare test data (no json format)
        test_data = {
            "method": "POST",
            "id": "8",
            "name": "arduino uno",
            "no_resi": "8595",
            "date_created": "2023-03-04 20:43:55",
        }

        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = test_data
            net_t = NetworkMethods(server_address='127.0.0.1', server_port=5000)
            _ret_val = net_t._encode_data_to_json(test_data)

            mock_dumps.assert_called_once_with(test_data)
            assert _ret_val == test_data
