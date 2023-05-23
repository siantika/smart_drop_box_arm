"""
    File           : main.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Apr, 2023
    Description    : 

        Driver of core application. It creates functions from 4 threads.
        It runs the operations needed by the core app and provide queue data
        as shared resources between threads.

    License: see 'licenses.txt' file in the root of project
"""

import os
import sys
import multiprocessing as mp

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(parent_dir, 'applications/operation_thread'))
sys.path.append(os.path.join(parent_dir, 'applications/lcd_thread'))
sys.path.append(os.path.join(parent_dir, 'applications/network_thread'))

from operation_thread import ThreadOperation
from lcd_thread import LcdThread
from network_thread import GetRequest, PostRequest

# shared resources, the names are perspective from opeartion thread
q_data_to_lcd = mp.Queue(10)
q_data_to_net = mp.Queue(10)
q_data_from_net = mp.Queue(10)

# create functions for running each thread
def opt_routine(q_data_to_lcd, q_data_from_net, q_data_to_net):
   '''
      Control all threads.
   
   '''
   opt_t = ThreadOperation()
   opt_t.set_queue_to_lcd_thread(q_data_to_lcd)
   opt_t.set_queue_from_net_thread (q_data_from_net)
   opt_t.set_queue_to_net_thread (q_data_to_net)
   opt_t.run()


def lcd_routine(q_data_to_lcd):
   '''
      Display data from operation thread
   '''
   lcd_t = LcdThread()
   lcd_t.set_queue_data(q_data_to_lcd)
   lcd_t.run()


def net_receive_routine(q_data_from_net):
   '''
      Polling requests GET from server every 5 secs   
   '''
   net_t = GetRequest()
   net_t.set_queue_data_to_operation(q_data_from_net)
   net_t.run()


def net_post_routine(q_data_to_net):
   '''
      send requests for DELETE stored no resi data in server
      and POST success items received plus photos in server.
   '''
   net_t = PostRequest()
   net_t.set_queue_data_from_operation(q_data_to_net)
   net_t.run()


process_lcd = mp.Process(target=lcd_routine, args=(q_data_to_lcd,))
process_opt = mp.Process(target=opt_routine, args=(q_data_to_lcd, q_data_from_net, q_data_to_net,))
process_net_get = mp.Process(target=net_receive_routine, args=(q_data_from_net,))
process_net_post = mp.Process(target=net_post_routine, args=(q_data_to_net, ))


# Driver code
if __name__ == '__main__':
   process_opt.start()
   process_lcd.start()
   process_net_get.start()
   process_net_post.start()
   
   process_opt.join()
   process_lcd.join()
   process_net_get.join()
   process_net_post.join()

