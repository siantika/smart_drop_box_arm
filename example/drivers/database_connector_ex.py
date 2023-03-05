import sys
sys.path.append('drivers/database_connector')

from database_connector import DatabaseConnector

# for spacing line
space = lambda:print()
splitter = lambda sym, iter :print(f"{sym}" * iter)

# endpoints
URL_GET     = 'http://localhost/smart_drop_box/get.php'
URL_POST    = 'http://localhost/smart_drop_box/post.php'
URL_UPDATE  = 'http://localhost/smart_drop_box/update.php'
URL_DELETE  = 'http://localhost/smart_drop_box/delete.php'
### DRIVER CODE

splitter('#',55)
space()
# get data from database based on 'id' parameter (OKAY test)
db = DatabaseConnector(URL_GET)
result = db.get_data('id','3')
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
db = DatabaseConnector(URL_POST)
print('Post data to database:')
print(
    db.post_data(
    name="step up", 
    no_resi="9978"
    )
)
# POST data to database in JSON format and return JSON response (BAD REQUEST test)
print('Post data to database (bad request):')
print(
    db.post_data(
    namesad="step up", 
    no_resddddi="9978"
    )
)
space()
splitter('*', 55)

# UPDATE data in database
# We can't update the same data content, it will return 404 status code (no data found)
db =  DatabaseConnector(URL_UPDATE)

id_update = 3
print(f'Updated data with id number {id_update}:')
print(db.update_data('id',str(id_update), name='arduino promini', no_resi='0023'))
space()
splitter('*',55)

# DELETE data in database
db =  DatabaseConnector(URL_DELETE)

id_delete = 11
print(f'Deleted data with id number {id_delete}:')
print(db.delete_data('id', str(id_delete)))
space()
splitter('#',55)