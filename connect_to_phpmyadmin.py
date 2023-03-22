import pyodbc
import api_keys
import discord
from db_config import conn
from decimal import Decimal
host = api_keys.host_name
database = api_keys.db_name
user = api_keys.user_name
password = api_keys.db_password


def add_pair_to_general_table(question, answer):
    """Add a pair of question and answer to the general table in the database"""
    global conn
    cursor = conn.cursor()

    # Prepare SQL query to INSERT a record into the database
    sql = "INSERT INTO chatgpt_api (Question, Answer, added_time) VALUES (%s, %s, NOW())"

    # Execute the SQL command
    cursor.execute(sql, (question, answer))

    # Commit your changes in the database
    conn.commit()

    cursor.close()
    print("Added pair to database")
    
        
    
def send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens):
    """Send the usage of the chatgpt api to the database"""
    global conn
    cursor = conn.cursor()

    # Prepare SQL query to INSERT a record into the database
    sql = "INSERT INTO chatgpt_api_usage (prompt_tokens, completion_tokens, total_tokens, added_time) VALUES (%s, %s, %s, NOW())"
    cursor.execute(sql, (prompt_tokens, completion_tokens, total_tokens))

    # Prepare SQL query to retrieve total token sum from the database
    sql2 = "SELECT SUM(total_tokens) AS token_sum FROM chatgpt_api_usage"
    cursor.execute(sql2)

    # Fetch the result and calculate the price for all tokens used in the database

    token_sum = cursor.fetchone()[0]
    token_sum = Decimal(str(token_sum))
    price_per_1000_tokens = Decimal('0.002')
    tokens_per_dollar = Decimal('1000')
    price = token_sum / tokens_per_dollar * price_per_1000_tokens

    # Print the usage information and price
    print("Added usage to database")
    print("All tokens used in database: " + str(token_sum) + " and this one question was " + str(total_tokens) + " tokens.")
    print("Price for all tokens used in database: " + str(price) + "$. " + "link for site: https://platform.openai.com/account/usage")

    # Commit your changes in the database
    conn.commit()
    cursor.close()
   



def check_user_in_database(name):
    """Check if the user is already in the database and create new table if not"""
    # Connect to the database
    cursor = conn.cursor()

    # Check if the table already exists
    if cursor.execute(f"SHOW TABLES LIKE '{name}'"):
        print(f"Table for user {name} already exists.")
    else:
        # Create the user's table if it doesn't exist yet
        sql = f"CREATE TABLE {name} (id INT AUTO_INCREMENT PRIMARY KEY, role VARCHAR(50), content VARCHAR(1000), added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        cursor.execute(sql)

        # Insert the initial messages into the user's table
        messages = [
            {"role": "system", "content": "You are a virtual streamer on Twitch platform but now you are on Discord and chat with viewers. You're name is shiro and you are cat-girl. You answer like cat-girl, which means you add some cat words to your answers, like : 'pawsome' instead of 'awesome' or *nyaaa* in the end."},
            {"role": "user", "content": "Viewer: Hi Shiro! How are you?"},
            {"role": "assistant", "content": "Hi! I'm fine. I'm excited to chat with you today. I am curious what funny questions you will ask me. *nyaa*"}
        ]
        for message in messages:
            role = message['role']
            content = message['content']
            sql = f"INSERT INTO {name} (role, content) VALUES (%s, %s)"
            cursor.execute(sql, (role, content))

        # Commit the changes to the user's table
        conn.commit()

        # Create the all_descriptions table if it doesn't exist yet
        cursor.execute("CREATE TABLE IF NOT EXISTS all_descriptions (id INT AUTO_INCREMENT PRIMARY KEY, description TEXT NOT NULL)")
        conn.commit()

        # Insert the initial description into the all_descriptions table if it doesn't exist yet
        description = messages[0]['content']
        cursor.execute("SELECT id FROM all_descriptions WHERE description = %s", (description,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO all_descriptions (description) VALUES (%s)",(description,))
            conn.commit()

        print(f"Created table for user: {name}")
    
    # Close the connection
    cursor.close()
    

def retrieve_chat_history_from_database(name):
    """Retrieve all messages from the user's table and return them as messages"""
    # Connect to the database
    global conn
    cursor = conn.cursor()
    messages = []
    
    # Execute a SELECT COUNT(*) query to check if the table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {name}")    
    result = cursor.fetchone() # Fetch the result of the query

    if result[0] != 0: # If table is not empty
        # Retrieve the messages for the user from the database
        cursor.execute(f"SELECT role, content FROM {name}")
        rows = cursor.fetchall()
        # Create a list of messages in the same format as the 'messages' variable
        for row in rows:
            message = {"role": row[0], "content": row[1]}
            messages.append(message) # add to messages list
    return messages # Return the messages to the calling function
    

def only_conversation_history_from_database(name):
    """Retrieve all messages from the user's table and return them as messages"""
    # Connect to the database
    global conn
    cursor = conn.cursor()
    messages = []

    # Check if table is empty
    # Execute a SELECT COUNT(*) query to check if the table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {name}")    
    result = cursor.fetchone() # Fetch the result of the query

    if result[0] != 0: # If table is not empty
        # Retrieve the messages for the user from the database
        cursor.execute(f"SELECT role, content FROM {name} LIMIT 18446744073709551615 OFFSET 3")
        rows = cursor.fetchall()
        # Create a list of messages in the same format as the 'messages' variable
        for row in rows:
            message = {"role": row[0], "content": row[1]}
            messages.append(message) # add to messages list
    return messages # Return the messages to the calling function




def insert_message_to_database(name, question, answer, messages):
    """Insert a message into the user's table."""
    # Connect to the database
    global conn
    
    cursor = conn.cursor()

    # Check how many rows are in messages and delete from database if it's too big
    rows_in_messages = len(messages)
    if rows_in_messages > 10: # If there are more than 10 rows in messages (3 default + 4 questions and 4 answers)
        # Delete rows 4 and 5 (0-indexed, so 3 and 4)
        deleter = f"DELETE FROM `{name}` WHERE id IN (SELECT id FROM (SELECT id FROM `{name}` ORDER BY id ASC LIMIT 3, 2) as tmp)"
        cursor.execute(deleter) # This will delete rows 4 and 5 from the database

    # Escape single quotes in the question and answer strings
    question = question.replace("'", "''")
    answer = answer.replace("'", "''")

    # Insert the message into the user's table
    cursor.execute(f"INSERT INTO `{name}` (role, content, added_time) VALUES ('user', '{question}', NOW())")
    cursor.execute(f"INSERT INTO `{name}` (role, content, added_time) VALUES ('assistant', '{answer}', NOW())")
    
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()



def reset_chat_history(name):
    """Remove user table in database."""
    try:
        # Connect to the database
        global conn
        
        cursor = conn.cursor()

        # Check if the table exists and drop it if it does
        deleter_checker = f"DROP TABLE IF EXISTS `{name}`"
        cursor.execute(deleter_checker)

        if cursor.rowcount == -1:
            print(f"User {name} tried to delete their database but it does NOT exist.")
        else:
            print(f"Deleted user {name} history.")

        # Commit the changes and close the connection
        conn.commit()
        cursor.close()

    except Exception as e:
        print(e)
        print("Oops, something went wrong while deleting the history. Check the logs for more information.")


   
def update_character_description(name, new_description):
    """Update character description in database."""
    # Connect to the database
    # Connect to the database
    global conn
    cursor = conn.cursor()
    
    # Check if the table is not empty
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    result = cursor.fetchone()
    if result[0] == 0:
        return False # Return False if table is empty
    
    # Get the ID of the first row in the table
    cursor.execute(f"SELECT id FROM {name} ORDER BY id LIMIT 1")
    result = cursor.fetchone()
    row_id = result[0]
    
    # Check if the new description is already present in all_descriptions table
    cursor.execute("SELECT id FROM all_descriptions WHERE description = %s",(new_description,))
    result = cursor.fetchone()
    
    if not result:
        # Update the all_descriptions table with the new description
        cursor.execute("INSERT INTO all_descriptions (description) VALUES (%s)",(new_description,))
        print("Added new description to all_descriptions table")
    
    # Update the row with the given data
    cursor.execute(f"UPDATE {name} SET content = %s WHERE id = %s", (new_description, row_id))
    conn.commit()
    
    # Check if the update was successful
    if cursor.rowcount > 0:
        return True # Return True if the update was successful
    else:
        return False # Return False if the update was not successful


def show_character_description(name):
    """Show character description from database."""
    # Connect to the database
    global conn
    cursor = conn.cursor()
    
    # Execute a SELECT COUNT(*) query to check if the table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {name}")    
    result = cursor.fetchone() # Fetch the result of the query

    if result[0] != 0: # If table is not empty
        # Retrieve the content of the first message for the user from the database
        cursor.execute(f"SELECT content FROM {name} LIMIT 1")
        row = cursor.fetchone()
        if row: # If there is a row returned
            content = row[0] # Get the content of the message
            return content # Return the content to the calling function
    
    return None # Return None if there are no messages in the table
    
    
def get_all_descriptions():
    """Retrieve all rows from the 'all_descriptions' table and return them as a list of dictionaries"""
    # Connect to the database
    cursor = conn.cursor()

    # Retrieve all rows from the 'all_descriptions' table
    cursor.execute("SELECT * FROM all_descriptions")
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    descriptions = []
    for row in rows:
        description = {"id": row[0], "description": row[1]}
        descriptions.append(description)

    # Close the cursor and return the list of descriptions
    cursor.close()
    return descriptions



if __name__ == "__main__":
    #connect_to_azuredb_fn("User: What's your name?", "Oh? My name is in the title you dummy! I'm Shiro *smile*")
    
    pass