import sys
import queue
sys.path.append('applications/storage_thread')
import threading
import logging 

lock = threading.Lock()

q_to_opt      = queue.Queue(5)
q_from_opt    = queue.Queue(5)
q_from_server = queue.Queue(5)
q_to_server   = queue.Queue(5)

def run_storage_thread(queue_to_opt, queue_from_opt, queue_from_server, queue_to_server):    
    str_t = StorageThread()
    str_t.set_queue(
            queue_from_thread_net  = queue_from_server, 
            queue_to_thread_opt    = queue_to_opt,
            queue_from_thread_opt  = queue_from_opt,
            queue_to_thread_net    = queue_to_server
         )
    while True:
        str_t.run()

def input_from_user(queue_from_server:queue.Queue, queue_from_t_opt:queue.Queue):
    while True:
        info_text = "Pilihan: \n \
            1. Set queue data from server.\n \
            2. Set queue data from opt thread.\n\
            input: "
        print()
        data = int(input(info_text))

        if data == 1:
            data = {
                'method' : 'update',
                'id'     : '124',
                'name'   : 'ESP8266',
                'no_resi': '0587'
            }
            with lock:
                queue_from_server.put(data)
        elif data == 2:
            data = {
                'method'      : 'get',
                'no_resi'     : '5696'
            }
            with lock:
                queue_from_t_opt.put(data)
        elif data == 3:
            data = {
                'method'       : 'delete',
                'no_resi'     : '9978'
            }
            with lock:
                queue_from_t_opt.put(data)
        else:
            logging.warning('input di luar jangkauan!')

def print_queue_data_to_thread_opt(queue_data_to_opt:queue.Queue):
    while True:
        if not queue_data_to_opt.empty():
            data_print = queue_data_to_opt.get()
            print(f"\n send data to thread opt: \n{data_print}")

def print_queue_data_to_thread_net(queue_data_to_net:queue.Queue):
    while True:
        if not queue_data_to_net.empty():
            data_print = queue_data_to_net.get()
            print(f"\n send data to thread Net: \n{data_print}")

thread_storage         = threading.Thread(target = run_storage_thread, args=(q_to_opt, q_from_opt,q_from_server,q_to_server, ))
thread_input_from_user = threading.Thread(target = input_from_user, args=(q_from_server, q_from_opt,  ))
thread_print_q_to_opt  = threading.Thread(target = print_queue_data_to_thread_opt, args=(q_to_opt, ))
thread_print_q_to_net  = threading.Thread(target = print_queue_data_to_thread_net, args=(q_to_server, ))

if __name__ == '__main__':
    thread_storage.start()
    thread_input_from_user.start()
    thread_print_q_to_opt.start()
    thread_print_q_to_net.start()