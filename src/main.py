"""
    File           : main.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Apr, 2023
    Description    : 

        Driver of core application. It creates functions from 4 threads.
        It runs the operations needed by the core app and provide queue data
        as shared resources between threads.

"""

import os
import sys
import multiprocessing as mp

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(parent_dir, 'src/applications/controller_app'))
sys.path.append(os.path.join(parent_dir, 'src/applications/display_app'))
sys.path.append(os.path.join(parent_dir, 'src/applications/data_transactions_app'))

from controller_app import ControllerApp
from display_app import DisplayApp
from data_transactions_app import HttpGetResiDataRoutineApp, HttpSendDataApp

# shared resources, the names are perspective from opeartion thread
q_data_to_display = mp.Queue(10)
q_data_to_data_access = mp.Queue(10)
q_data_from_data_access = mp.Queue(10)

# create functions for running each thread
def controller_routine(q_data_to_display, q_data_from_data_access, q_data_to_data_data_access):
   '''
      Control all threads.
   '''
   controller = ControllerApp()
   controller.set_queue_data(q_data_to_display,
                             q_data_from_data_access,
                             q_data_to_data_data_access)
   controller.run()


def display_routine(q_data_to_display):
   '''
      Display data from controller thread
   '''
   display = DisplayApp()
   display.set_queue_data(q_data_to_display)
   display.run()


def get_data_routine(q_data_from_data_access):
   '''
      Handle data routine every 5 secs
   '''
   get_routine = HttpGetResiDataRoutineApp()
   get_routine.set_queue_data(q_data_from_data_access)
   get_routine.run()


def data_transactions_routine(q_data_to_data_access):
   '''
      Handle data transactions ( to server )
   '''
   send_data = HttpGetResiDataRoutineApp()
   send_data.set_queue_data(q_data_to_data_access)
   send_data.run()


thread_display = mp.Process(target=display_routine, args=(q_data_to_display,))
thread_controller= mp.Process(target=controller_routine, args=(q_data_to_display, 
                                                                q_data_from_data_access,                                                                
                                                                 q_data_to_data_access,))
thread_get_routine = mp.Process(target=get_data_routine, args=(q_data_from_data_access,))
thread_data_transaction = mp.Process(target=data_transactions_routine, args=(q_data_to_display, ))


# Driver code
if __name__ == '__main__':
   thread_controller.start()
   thread_display.start()
   thread_get_routine.start()
   thread_data_transaction.start()
   
   thread_controller.join()
   thread_display.join()
   thread_get_routine.join()
   thread_data_transaction.join()

