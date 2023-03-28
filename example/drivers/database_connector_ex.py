'''

'''

import sys
sys.path.append('drivers/database_connector')
sys.path.append('example/drivers')

from database_connector import DatabaseConnector

# for spacing line
space = lambda:print()
splitter = lambda sym, iter :print(f"{sym}" * iter)

# endpoints
URL = 'https://dropbox.smart-monitoring.my.id/' ### remeber to put backslash in end of url!
endpoint_paths = {'get':'get.php','update':'update.php','delete':'delete.php','post':'post.php', 'success_items' : 'success_items.php'}
secret_key  = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1'

### DRIVER CODE
splitter('#',55)
space()

db = DatabaseConnector(URL, endpoint_paths)

## set encoded token
db.set_encode(
    secret= secret_key,
    algo= "HS256",
    token_type= "Bearer"
)

print(db.encode())

  
print('Post data to database:')
print(
    db.post_data(
{   "name":"ST LINK ", 
    "no_resi":"0023"}, 'post'
    )
)

# POST data to database in JSON format and return JSON response (BAD REQUEST test)
print('Post data to database (bad request):')
print(
    db.post_data(
{    "nameasd":"step up", 
    "no_resi":"9978"}, 'post'
    )
)

# POST data to 'success_items' (multipart/form-data).
print ("Post database with picture")
test_data = {
    'name' : 'mouse',
    'no_resi' : '9638',
    'date_ordered' : '2023-03-23 14:39:01'
}

with open("/home/oem/PROJECTS/smart_drop_box/software/drop_box/example/drivers/lcd_bener.jpg", "rb" ) as f:
    test_photo = f.read()

# Photo file should has value in tuple such as below !
photo_payload = {'photo' : ('lcd_bener',test_photo)}
test_data.update(photo_payload)
# print (f"payload data with photo {test_data}")

res =db.post_data(
    test_data, 'success_items'
)
print(res)

space()

  
# get data from database based on 'no resi' parameter (OKAY test)

result = db.get_data('no_resi','')
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
print(db.update_data({'old_resi':old_resi, 'name':'arduino promini', 'new_resi':'2310'}))
space()
splitter('*',55)

# DELETE data in database

no_resi = '2310'
print(f'Deleted data with id number {no_resi}:')
print(db.delete_data('no_resi', str(no_resi)))
space()
splitter('#',55)