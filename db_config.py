# db_config.py
import pyodbc
import api_keys
server = api_keys.server_name
database = api_keys.db_name
username = api_keys.user_name
password = api_keys.db_password
driver= '{ODBC Driver 18 for SQL Server}'

# Define the global connection object
conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
