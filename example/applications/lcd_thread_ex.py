import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'applications/lcd_thread'))
from lcd_app import LcdThread
import queue
import threading
import logging

lock = threading.Lock()
'''
Make 2 threads.
    1) Input queue data from CLI.
       * input :
        + is_enter_keypad (list)  : 0 or 1 (int)
        + keypad_char_data (list) : char (str) 
        + data_display (list)     : 2 items str
    2) lcd thread
'''
#shared resources
queue_data_thread_opt = queue.Queue(5)

def input_from_user(data_queue: queue.Queue):
    while True:
        info_text = "Pilihan: \n \
            1. Set keypad cmd.\n \
            2. Set routine cmd (single char of no resi).\n\
            3. Set routine cmd (4 digits resi).\n\
            input: "
        print()
        data = int(input(info_text))

        if data == 1:
            input_data = {
                'cmd'     : 'routine',
                'payload' : ['itms stored: 12', 'itms waiting: 5']
            }
            with lock:
                data_queue.put(input_data)
        elif data == 2:
            input_data = {
                'cmd'     : 'keypad',
                'payload' : ['Masukan resi:', '0']
            }
            with lock:
                data_queue.put(input_data)
        elif data == 3:
            input_data = {
                'cmd'     : 'keypad',
                'payload' : ['Masukan resi:', '0056']
            }
            with lock:
                data_queue.put(input_data)
        else:
            logging.warning('input di luar jangkauan!')

#create function
def lcd_process(data_queue):
    lcd_t = LcdThread()
    lcd_t.set_queue_data(data_queue)
    lcd_t.run()

def test_lcd_process(data_queue: queue.Queue):
    while True:
        try:
            data = data_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue
        print(f"\ndata LCD: {data}")


#create threads
thread_lcd = threading.Thread(target=lcd_process, args=(queue_data_thread_opt, ))
thread_input = threading.Thread(target= input_from_user,  args= (queue_data_thread_opt,))
test_thread_lcd = threading.Thread(target=test_lcd_process, args= (queue_data_thread_opt,))

if __name__ == '__main__':
   thread_input.start()
   thread_lcd.start()
   test_thread_lcd.start()
