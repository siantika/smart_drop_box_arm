'''
    If server requeires Auth, you need to perform encoding methods.
    eg: 
    "
        set_encode()
        encode()
    "

'''

import sys
sys.path.append('drivers/database_connector')

from database_connector import DatabaseConnector

# for spacing line
space = lambda:print()
splitter = lambda sym, iter :print(f"{sym}" * iter)

# secret
LOCAL_SECRET = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

# endpoints
URL = 'http://127.0.0.1/smart_drop_box/' ### remeber to put backslash in end of url!
endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php'}

### DRIVER CODE

splitter('#',55)
space()

db = DatabaseConnector(URL, endpoint_paths)


# get data from database based on 'id' parameter (OKAY test)

result = db.get_data('id','50')
print("********** Get data (TEST OKAY): **********")
print("* Get data from database [message]:")
print("  ---->",result[1])
print("* Get data from database [status_code]:")
print("  ---->",result[0])
space()

# get data from database based on 'id' parameter (ERROR NOT FOUND test)
result = db.get_data('id','9000000')
print("********** Get data (TEST ERROR NOT FOUND ): **********")
print("* Get data from database [data]:")
print("  ---->",result[1])
print("* Get data from database [status_code]:")
print("  ---->",result[0])
space()

# get data from database based on 'id' parameter (BAD REQUEST test)
result = db.get_data('ida3q4q34','900000')
print("********** Get data (TEST BAD REQUEST ): **********")
print("* Get data from database [data]:")
print("  ---->",result[1])
print("* Get data from database [status_code]:")
print("  ---->",result[0])
space()
splitter('*',55)

# POST data to database in JSON format and return JSON response {'status' and 'new id inserted'}
db.set_encode(
    secret= LOCAL_SECRET,
    algo='HS256',
    token_type='Bearer'
)
db.encode(
    {"":""}
)
    
print('Post data to database:')
print(
    db.post_data(
{   "name":"ST LINK ", 
    "no_resi":"0023"}
    )
)

# POST data to database in JSON format and return JSON response (BAD REQUEST test)
print('Post data to database (bad request):')
print(
    db.post_data(
{    "nameasd":"step up", 
    "no_resi":"9978"}
    )
)
space()
splitter('*', 55)

# UPDATE data in database
# We can't update the same data content, it will return 404 status code (no data found)
db.set_encode(
    secret= LOCAL_SECRET,
    algo='HS256',
    token_type='Bearer'
)
db.encode(
    {"":""}
)

id_update = 53
print(f'Updated data with id number {id_update}:')
print(db.update_data({'id':'id_update', 'name':'arduino promini', 'no_resi':'0023'}))
space()
splitter('*',55)

# DELETE data in database
db.set_encode(
    secret= LOCAL_SECRET,
    algo='HS256',
    token_type='Bearer'
)
db.encode(
    {"":""}
)

id_delete = 85
print(f'Deleted data with id number {id_delete}:')
print(db.delete_data('id', str(id_delete)))
space()
splitter('#',55)