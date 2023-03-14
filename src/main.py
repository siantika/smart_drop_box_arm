import sys
import json
sys.path.append('applications/storage_thread')
from storage_thread import StorageThread

str_t = StorageThread()

data = {
    "method" : "GET",
    "id"     : 49,

}

ret = str_t.send_request(
              data
)

print(ret[0])