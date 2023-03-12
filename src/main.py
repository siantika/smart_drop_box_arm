import sys
import queue
sys.path.append('applications/network_thread')
from network_thread import NetworkThread

q_read = queue.Queue()
q_send = queue.Queue()
net = NetworkThread(
        server_address= 'www.google.co.id', 
        server_port= 80, 
        queue_to_read= q_read, 
        queue_to_send = q_send
    )

net.run()