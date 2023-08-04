import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'applications/operation_thread'))
sys.path.append(os.path.join(parent_dir, 'applications/lcd_thread'))

from controller_app import ThreadOperation
from lcd_app import LcdThread

import multiprocessing as mp

q_data_to_lcd = mp.Queue(10)

# create functions
def opt_routine(q_data_to_lcd):
   opt_t = ThreadOperation()
   opt_t.set_queue_to_lcd_thread(q_data_to_lcd)
   opt_t.run()


def lcd_routine(q_data_to_lcd):
   lcd_t = LcdThread()
   lcd_t.set_queue_data(q_data_to_lcd)
   lcd_t.run()

process_lcd = mp.Process(target=lcd_routine, args=(q_data_to_lcd,))
process_opt = mp.Process(target=opt_routine, args=(q_data_to_lcd,))

if __name__ == '__main__':
   process_opt.start()
   process_lcd.start()
