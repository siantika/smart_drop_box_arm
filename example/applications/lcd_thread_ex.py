import sys
import time
sys.path.append('applications/lcd_thread')
from lcd_thread import LcdThread
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

def input_from_user(keypad_flag:list, keypad_char:queue.Queue, data_to_be_displayed: queue.Queue):
    while True:
        info_text = "Pilihan: \n \
            1. Set is_enter_keypad.\n \
            2. Set keypad_char_data.\n\
            3. Set data display.\n \
            input: "
        print()
        data = int(input(info_text))

        if data == 1:
            input_data = int(input("Masukan data untuk is_enter_keypad (0 atau 1): "))
            with lock:
                keypad_flag[0] = input_data
        elif data == 2:
            input_data = str(input("Masukan data untuk keypad_char_data : "))
            with lock:
                keypad_char.put(input_data)
        elif data == 3:
            input_data_1 = str(input("Masukan first line data  : "))
            input_data_2 = str(input("Masukan second line data : "))
            listed = [input_data_1, input_data_2]
            with lock:
                data_to_be_displayed.put(listed)
        else:
            logging.warning('input di luar jangkauan!')

def print_keypad_flag(keypad_flag:list):
    while True:
        with lock:
            print(f"\nkeypad flag: {keypad_flag[0]}")
        time.sleep(2)
        
#shared resources
g_keypad_flag = [0]
g_keypad_char_data = queue.Queue(4)
g_data_display = queue.Queue(5)

#create function
def lcd_process(
                _dev_addr,
                _bus_addr,
                _keypad_flag,
                _keypad_char_data,
                _queue_data_read
              ):
    lcd_t = LcdThread(
        dev_addr=_dev_addr,
        bus_addr= _bus_addr,
        keypad_flag=_keypad_flag,
        keypad_char_data = _keypad_char_data,
        queue_data_read= _queue_data_read
    )
    while True:
        lcd_t.run()

#create threads
thread_lcd = threading.Thread(
    target=lcd_process, 
    args=(0x27,0,g_keypad_flag,g_keypad_char_data,g_data_display, ) # Remember put (args, ) for pass the list!
    )
thread_input = threading.Thread(
    target=input_from_user, 
    args=(g_keypad_flag, g_keypad_char_data, g_data_display, )
    )


if __name__ == '__main__':
   thread_input.start()
   thread_lcd.start()
