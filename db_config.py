import pymysql
import api_keys

host = api_keys.host_name
database = api_keys.db_name
user = api_keys.user_name
password = api_keys.db_password

# Define the global connection object
conn = pymysql.connect(host=host, user=user, password=password, database=database)
