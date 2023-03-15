import sys
import queue
sys.path.append('applications/storage_thread')
from storage_thread import StorageThread

q_to_opt      = queue.Queue(5)
q_from_opt    = queue.Queue(5)
q_from_server = queue.Queue(5)
q_to_server   = queue.Queue(5)

# q_from_opt.put(
#     {
#         # "method"  : "get",
#         # "id" : 93
#         # "name"    : "SHT11",
#         # "no_resi" : "0502"
#     }
# )

str_t = StorageThread()
str_t.set_queue(q_from_opt, q_to_opt, q_from_server, q_to_server)
print(str_t._get_secret())
#print(q_to_opt.get())
