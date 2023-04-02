"""
    File           : main.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Apr, 2023
    Description    : 

        Driver of core application. It creates functions from 3 threads, run it, and
        assigned queue data for shared resources between threads.

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
from network_thread import NetworkThread


# shared exchange data from operation tread to lcd thread.
q_data_to_lcd = mp.Queue(10)
q_data_to_net = mp.Queue(10)
q_data_from_net = mp.Queue(10)

# create functions
def opt_routine(q_data_to_lcd, q_data_from_net, q_data_to_net):
   opt_t = ThreadOperation()
   opt_t.set_queue_to_lcd_thread(q_data_to_lcd)
   opt_t.set_queue_from_net_thread (q_data_from_net)
   opt_t.set_queue_to_net_thread (q_data_to_net)
   opt_t.run()


def lcd_routine(q_data_to_lcd):
   lcd_t = LcdThread()
   lcd_t.set_queue_data(q_data_to_lcd)
   lcd_t.run()


def net_routine(q_data_to_net, q_data_from_net):
   net_t = NetworkThread()
   net_t.set_queue_from_operation(q_data_to_net)
   net_t.set_queue_to_operation(q_data_from_net)
   net_t.run()


process_lcd = mp.Process(target=lcd_routine, args=(q_data_to_lcd,))
process_opt = mp.Process(target=opt_routine, args=(q_data_to_lcd, q_data_from_net, q_data_to_net,))
process_net = mp.Process(target=net_routine, args=(q_data_to_net, q_data_from_net,))

#driver function
if __name__ == '__main__':
   process_opt.start()
   process_lcd.start()
   process_net.start()
   
   process_opt.join()
   process_lcd.join()
   process_net.join()

