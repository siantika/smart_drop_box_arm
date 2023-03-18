import sys
sys.path.append('applications/opt_thread')
sys.path.append('applications/lcd_thread')
from opt_thread import ThreadOperation
from lcd_thread import LcdThread

from queue import Queue
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
