import sys
sys.path.append('drivers/database_connector')
from database_connector import DatabaseConnector

db = DatabaseConnector('https://localhost.com')

db.patch_data(
    param_matching= '',
    param_matching_value= '',
    param_patched= '',
    param_patched_value= '',
)
