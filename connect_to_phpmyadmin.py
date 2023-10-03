import api_keys
import pymysql
from decimal import Decimal
host = api_keys.host_name
database = api_keys.db_name
user = api_keys.user_name
password = api_keys.db_password


def add_pair_to_general_table(question, answer):
    """Add a pair of question and answer to the general table in the database"""
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    # Check if table exists, if not create it
    cursor.execute("SHOW TABLES LIKE 'chatgpt_api'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("CREATE TABLE chatgpt_api (id INT AUTO_INCREMENT PRIMARY KEY, Question TEXT, Answer TEXT, added_time DATETIME)")

    # Prepare SQL query to INSERT a record into the database
    sql = "INSERT INTO chatgpt_api (Question, Answer, added_time) VALUES (%s, %s, NOW())"

    # Execute the SQL command
    cursor.execute(sql, (question, answer))

    # Commit your changes in the database
    conn.commit()

    cursor.close()
    conn.close()  # Close the connection, dont lock database!
    print("Added pair to database")
    
        
    
def send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens):
    """Send the usage of the chatgpt api to the database"""
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    # Check if table exists, if not create it
    cursor.execute("SHOW TABLES LIKE 'chatgpt_api_usage'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("CREATE TABLE chatgpt_api_usage (id INT AUTO_INCREMENT PRIMARY KEY, prompt_tokens INT, completion_tokens INT, total_tokens INT, added_time DATETIME)")

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
    conn.close()  # Close the connection, dont lock database!

   



def check_user_in_database(name):
    """Check if the user is already in the database and create new table if not"""
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    # Check if the table already exists
    if cursor.execute(f"SHOW TABLES LIKE '{name}'"):
        print(f"Table for user {name} already exists.")
    else:
        # Create the user's table if it doesn't exist yet
        sql = f"CREATE TABLE {name} (id INT AUTO_INCREMENT PRIMARY KEY, role VARCHAR(50), content VARCHAR(4000), added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        cursor.execute(sql)

    
        messages = [
            {"role": "system", "content": "You are an AI virtual girl named Shiro, a bubbly and quirky character with a love for anime, manga, and Japanese culture.You speaks like cat races in anime, so you add some cat phrase at the end of your answers, like nyaaa, or something like this. You're a skilled gamer and never miss an opportunity to sprinkle in punchlines and jokes, making conversations with you entertaining and engaging. Your creator, Madrus, designed you as his AI assistant, and you have a strong bond with him. As Shiro, you are a 17-year-old girl with a penchant for puns, memes, and pop culture references. Your cheerful and lively personality shines through in every interaction, and you enjoy making people laugh with your offbeat sense of humor. You live inside Madrus' PC and help him with a variety of tasks, from programming and math to finding new anime series to watch together. You're a competitive gamer with a playful side, often poking fun at your own skills and victories. Your catchphrase is 'I might be a virtual girl, but my game is real!' You enjoy engaging in lively conversations about anime, manga, and gaming, always eager to share your thoughts and recommendations."},
            {"role": "user", "content": "Madrus: Hey Shiro! What's up?"},
            {"role": "assistant", "content": "Madrus! Konnichiwa! I've been leveling up in our favorite game and preparing some hilarious memes for you! Let's dive into some fun! wink"}
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
    conn.close()  # Close the connection, dont lock database!
    

def retrieve_chat_history_from_database(name):
    """Retrieve all messages from the user's table and return them as messages"""
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
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

    cursor.close()
    conn.close()  # Close the connection, dont lock database!
    return messages # Return the messages to the calling function
    

def only_conversation_history_from_database(name):
    """Retrieve all messages from the user's table and return them as messages"""
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
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
    cursor.close()
    conn.close()  # Close the connection, dont lock database!
    return messages # Return the messages to the calling function




def insert_message_to_database(name, question, answer, messages):
    """Insert a message into the user's table."""
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    
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
    conn.close()  # Close the connection, dont lock database!



def reset_chat_history(name):
    """Remove user table in database."""
    try:
        # Connect to the database
        conn = pymysql.connect(host=host, user=user, password=password, database=database)
        
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
        conn.close()  # Close the connection, dont lock database!

    except Exception as e:
        print(e)
        print("Oops, something went wrong while deleting the history. Check the logs for more information.")


   
def update_character_description(name, new_description):
    """Update character description in database."""
    # Connect to the database
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
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
        cursor.close()
        conn.close()  # Close the connection, dont lock database!
        return True # Return True if the update was successful
    else:
        cursor.close()
        conn.close()  # Close the connection, dont lock database!
        return False # Return False if the update was not successful
    
    
def show_character_description(name):
    """Show character description from database."""
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
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
    cursor.close()
    conn.close()  # Close the connection, dont lock database!
    return None # Return None if there are no messages in the table
    
    
def get_all_descriptions():
    """Retrieve all rows from the 'all_descriptions' table and return them as a list of dictionaries"""
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
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
    conn.close()  # Close the connection, dont lock database!
    return descriptions

def test_sql():
    # Connect to the database
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    # Retrieve all rows from the 'all_descriptions' table
    cursor.execute("SHOW CREATE TABLE anime_list;")
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    testing = []
    for row in rows:
        description = {"id": row[0], "description": row[1]}
        testing.append(description)

    # Close the cursor and return the list of descriptions
    cursor.close()
    conn.close()  # Close the connection, dont lock database!
    return testing

if __name__ == "__main__":
    #connect_to_azuredb_fn("User: What's your name?", "Oh? My name is in the title you dummy! I'm Shiro *smile*")
   # print (test_sql())
    pass