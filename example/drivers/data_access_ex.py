"""
 File: data access example 
 Author: I Putu Pawesi Siantika, S.T.
 Date: July 2023

 This file is intended for give an example of how to
 use data access especially http access.

 prerequisites:
    packages:
        requests: http requests methods.
    
"""
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/data_access'))
sys.path.append(os.path.join(parent_dir, 'example/drivers'))

from data_access import HttpDataAccess

# for spacing line
space = lambda:print()
splitter = lambda sym, iter :print(f"{sym}" * iter)

# endpoints
URL = 'https://dropbox.smart-monitoring.my.id/' ### remeber to put backslash in end of url!
endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php', 'post-multipart' : 'success_items.php'}
TEST_GENERATED_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
test_http_header = {'content-type':'application/json', 'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cGUiOiJKV1QifQ.eyJuYW1lIjoic2lhbiIsImVtYWlsIjoic2lhbkBtZWRpYXZpbWFuYUBnbWFpbC5jb20ifQ._nDoC3oUmgjzHwg8xpIwMJV2oQFbxWWyQ1inCL6dRrw'}
# add user agent
test_http_header['user-agent'] = user_agent

splitter('#',55)
space()

data = HttpDataAccess(URL, endpoint_paths, TEST_GENERATED_TOKEN)
  
print('Post data to database:')
print(
    data.post(payload={"name":"ST LINK ","no_resi":"0023"}, endpoint='post', http_header=test_http_header)
)

# POST data to database in JSON format and return JSON response (BAD REQUEST test)
print('Post data to database (bad request):')
print(
    data.post(payload={"naddme":"ST LINK ","no_resi":"0023"}, endpoint='post', http_header=test_http_header)
)


# POST data to 'success_items' (multipart/form-data).
print ("Post database with picture")
test_data = {
    'name' : 'mouse',
    'no_resi' : '3691',
    'date_ordered' : '2023-03-23 14:39:01'
}

# created photo in bin format
with open("/home/sian/sian/projects/smart_drop_box/software/drop_box/example/drivers/lcd_bener.jpg", "rb" ) as f:
    test_photo = f.read()

# Photo file should has value in tuple such as below !
photo_payload = {'photo': ('lcd_barddu.jpg', test_photo)}
res =data.post(
    payload=test_data,
    endpoint='post-multipart',
    http_header=test_http_header,
    file=photo_payload, 
    time_out = 10,
)
print(res)
space()

# get data from database based on 'no resi' parameter (OKAY test)
result = data.get({'no_resi' : '9987'}, 'get', test_http_header)
print(result)
print("********** Get data (TEST OKAY): **********")
print("* Get data from database [message]:")
print("  ---->",result[1])
print("* Get data from database [status_code]:")
print("  ---->",result[0])
space()
splitter('*', 55)

# UPDATE data in database
# We can't update the same data content, it will return 404 status code (no data found)
old_resi = '0023'
print(f'Updated data {old_resi} with new_resi 2310:')
print(data.update({'old_resi':old_resi, 'name':'arduino promini', 'new_resi':'2310'}, 'update',
                  test_http_header))
space()
splitter('*',55)

# DELETE a data in database
no_resi = '2310'
print(f'Deleted data with id number {no_resi}:')
print(data.delete({'no_resi' : no_resi}, 'delete', test_http_header))
space()
splitter('#',55)