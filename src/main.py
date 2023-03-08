import sys
sys.path.append('drivers/database_connector')
from database_connector import DatabaseConnector

db = DatabaseConnector('https://localhost.com')

token = db.encode(
            payload_data =
            {
            "name":"sian",
            "email":"sian@mediavimana@gmail.com"
            },
        secret = '0534f1025fc5b2da9a41be5951116816bedf30f336b65a8905716eccb800b8c1', 
        algo = 'HS256',
        token_type='Bearer',
        )

print(token)
