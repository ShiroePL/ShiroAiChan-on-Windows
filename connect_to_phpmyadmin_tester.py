import mysql.connector
import time
import db_config
from db_config import conn
from decimal import Decimal
import csv
#start rime

table = 'chatgpt_api'

with open('result.csv', 'r', encoding='utf-8') as csvfile:
    cursor = conn.cursor()
    cursor.execute(f'TRUNCATE TABLE {table}') # Optional: truncate table before inserting data
    next(csvfile) # Skip header
    for row in csv.reader(csvfile):
        cursor.execute(f'INSERT INTO {table} (QuestionID, Question, Answer, added_time) VALUES (%s, %s, %s, %s)', (row[0], row[1], row[2], row[3]))

conn.commit()