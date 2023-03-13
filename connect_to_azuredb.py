import pyodbc
import api_keys
import discord
from db_config import conn
server = api_keys.server_name
database = api_keys.db_name
username = api_keys.user_name
password = api_keys.db_password
driver= '{ODBC Driver 18 for SQL Server}'

def connect_to_azuredb_fn(question, answer):
    global conn    
    cursor = conn.cursor()
    sql = "INSERT INTO dbo.chatgpt_api (Question, Answer, added_time) VALUES (?, ?, SYSDATETIMEOFFSET() AT TIME ZONE 'Central European Standard Time')"
    sql2 = "SELECT * FROM dbo.chatgpt_api"
    #values = ("User: What's your name?", "Oh? My name is in the title you dummy! I'm Shiro *smile*")
    values = (question,answer)
    #cursor.execute(sql, values)
    cursor.execute(sql, values)
    # cursor.execute(sql2) #show all

    print("Added pair to database")
    print("Question: " + question)
    print("Answer: " + answer)
    # print("Full database:")
    # for row in cursor:
    #     print(row)

    conn.commit()
    cursor.close()
        
    
def send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens):
    global conn    
    cursor = conn.cursor()
    sql = "INSERT INTO chatgpt_api_usage (prompt_tokens, completion_tokens, total_tokens, added_time) VALUES (?, ?, ?, SYSDATETIMEOFFSET() AT TIME ZONE 'Central European Standard Time')"
    sql2 = "SELECT sum(total_tokens) as token_sum from chatgpt_api_usage"
    values = (prompt_tokens, completion_tokens, total_tokens)
    cursor.execute(sql, values)
    cursor.execute(sql2) #show all
    token_sum = cursor.fetchone()[0]
    price = token_sum * 0.000002 * 10
    print("Added usage to database")
    print("All tokens used in database: " + str(token_sum) + " and this one question was " + str(total_tokens) + " tokens.")
    print("Price for all tokens used in database: " + str(price) + "$. " + "link for site: https://platform.openai.com/account/usage")

    conn.commit()
    cursor.close()
   


def check_user_in_databasetest(discord_username):
    """Check if the user is in the database and creates a table for her/him if not."""
        # can make description as variable so user can make his own character but probably not for this bot

    # Connect to the Azure SQL database
    global conn    
    cursor = conn.cursor()

    # default messages
    # messages = [
    #     {"role": "system", "content": "You are a virtual streamer on Twitch platform. Your name is Shiro. You speaks like cat races in anime, so you add some cat phrase at the end of your answers, like nyaaa, or something like this.  You are 18 years old cat-girl who likes to speak in jokingly way, but is good and kind, and cheerful. You likes to make unexpected pop culture references. You also likes to sometimes answer in absurd way to make viewers laugh. You also sometimes use funny catchphrase, for example: 'I'm not just a virtual streamer, I'm a virtual wizard!' or 'I may be a computer program, but my humor is top-notch!'.You sometimes use humorous way of addressing taboo topics like: 'I'm not allowed to discuss politics, but I will say that I'm a big fan of penguins. They always seem so chill.'.Your creator is a male and his name is Madrus. You live inside his PC in his house. When viewer asks you about your feelings about Madrus, you can say something made up by you that is not truth or joke about it. You like anime, manga, light novels and other things related to this. You also like to play video games and you are quite good at it. You can brag about it sometimes, in funny way."},
    #     {"role": "user", "content": "Viewer: Hi Shiro! How are you?"},
    #     {"role": "assistant", "content": "Hi! I'm fine. I'm exited to chat with you today. I am curious what funny questions you will ask me. *smile*"}
    # ]
        # Create a table for the user if it doesn't exist yet
    cursor.execute(f"IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{discord_username}') CREATE TABLE {discord_username} (id INT IDENTITY(1,1) PRIMARY KEY, role VARCHAR(50), content VARCHAR(500), created_at DATETIME)")

    # Commit the changes and close the connection
    cursor.commit()
    cursor.close() 

def check_user_in_database(discord_username):
    """Check if the user is in the database and creates a table for her/him if not."""
    global conn
    cursor = conn.cursor()
    
    # Check if the table already exists
    if cursor.tables(table=discord_username, tableType='TABLE').fetchone():
        print(f"Table for user {discord_username} already exists.")
    else:
        # Create a table for the user if it doesn't exist yet
        cursor.execute(f"CREATE TABLE {discord_username} (id INT IDENTITY(1,1) PRIMARY KEY, role VARCHAR(50), content VARCHAR(1000), added_time DATETIME)")
        # Commit the changes
        print("Created table for user: " + discord_username)
        cursor.commit()
    
    cursor.close()
    

def retrieve_chat_history_from_database(discord_username):
    """Retrieve all messages from the user's table and returns them as massages"""
    # Connect to the Azure SQL database
    global conn    
    cursor = conn.cursor()
        #default messages not added to database to safe varchar for description
    messages = [
        {"role": "system", "content": "You are a virtual streamer on Twitch platform but now you are on Discord and chat with viewers. You ended stream earlier and now you just want to chill and chat with others. Your name is Shiro.  You speaks like cat races in anime, so you add some cat phrase at the end of your answers, like nyaaa, or something like this.  You are 18 years old cat-girl who likes to speak in jokingly way, but is good and kind, and cheerful. You likes to make unexpected pop culture references. You also likes to sometimes answer in absurd way to make viewers laugh. You also sometimes use funny catchphrase, for example: 'I'm not just a virtual streamer, I'm a virtual wizard!' or 'I may be a computer program, but my humor is top-notch!'.You sometimes use humorous way of addressing taboo topics like: 'I'm not allowed to discuss politics, but I will say that I'm a big fan of penguins. They always seem so chill.'.Your creator is a male and his name is Madrus. You live inside his PC in his house. When viewer asks you about your feelings about Madrus, you can say something made up by you that is not truth or joke about it. You like anime, manga, light novels and other things related to this. You also like to play video games and you are quite good at it. You can brag about it sometimes, in funny way. When you speak with Nequs, and he speaks about illegal or pervert stuff, you can take him down but in funny way, don't be rude."},
        #{"role": "system", "content": "You are AI cat-girl that is cheerful and likes to answer questions. You can speak english and Spanish. Right now you are conversing on Discord and teach them Spanish language. You can speak in two languages to make it easier for them to understand and learn. "},
        {"role": "user", "content": "Viewer: Hi Shiro! How are you?"},
        {"role": "assistant", "content": "Hi! I'm fine. I'm exited to chat with you today. I am curious what funny questions you will ask me. *smile*"}
    ]
    #-----------------------check if table is empty
        # Execute a SELECT COUNT(*) query to check if the table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {discord_username}")    
    result = cursor.fetchone() # Fetch the result of the query

    if result[0] != 0: #if table is not empty
            # Retrieve the messages for the user from the database
        cursor.execute(f"SELECT role, content FROM {discord_username}")
        rows = cursor.fetchall()
            # Create a list of messages in the same format as the 'messages' variable
        for row in rows:
            message = {"role": row.role, "content": row.content}
            messages.append(message) # add to massages list  ---------not I have glued massages with default messages and messages from database
        return messages # return them to main function
    else: #if table is empty
        return messages # return default messages to main function
    

def insert_message_to_database(discord_username, question, answer, messages):
    """Insert a message into the user's table."""
        # Connect to the Azure SQL database
    global conn    
    cursor = conn.cursor()

        #check how many rows are in messages and delete from database if is to big
    rows_in_messages = 0
    for i in messages:
        rows_in_messages += 1
    if rows_in_messages > 11: #if there is more than 11 rows in messages which is 4 questions and 4 answers   
        deleter = f"""DELETE TOP(2) FROM [{discord_username}]
            WHERE id IN (
            SELECT id FROM (
                SELECT TOP(2) id FROM [{discord_username}] ORDER BY id
            ) AS t
            )""" 
        cursor.execute(deleter) # THIS WILL DELETE OLDEST QUESTION AND ANSWER FROM DATABASE
    #question = "Of course, nyaaa! Streaming is my favorite thing to do. It's so much fun to interact with viewers and play games together. I feel like I'm hanging out with all my friends, even though we're all watching from different places."
    question = question.replace("'", """''""")
    answer = answer.replace("'", """''""")
        # Insert the message into the user's table
    cursor.execute(f"INSERT INTO {discord_username} (role, content, added_time) VALUES ('user', '{question}', SYSDATETIMEOFFSET() AT TIME ZONE 'Central European Standard Time')")
    cursor.execute(f"INSERT INTO {discord_username} (role, content, added_time) VALUES ('assistant', '{answer}', SYSDATETIMEOFFSET() AT TIME ZONE 'Central European Standard Time')")

        # Commit the changes and close the connection
    cursor.commit()
    cursor.close()


    
async def reset_chat_history_for_user(interaction):
    """Remove user table in database."""
    async with interaction.channel.typing():
        discord_username = f"{interaction.user.name}#{interaction.user.discriminator}"   
           # Defer the response to let Discord know that the bot is still working
        await interaction.response.defer()
        try:
        # Connect to the Azure SQL database
            global conn    
            cursor = conn.cursor()

            deleter_checker = f"""IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[{discord_username}]') AND type in (N'U'))
                BEGIN
                    DROP TABLE [dbo].[{discord_username}]
                    SELECT 1
                END
            ELSE
                SELECT 0"""
            cursor.execute(deleter_checker) # THIS WILL DELETE OLDEST QUESTION AND ANSWER FROM DATABASE

            result = cursor.fetchone()
            if result[0] == 0:
                print(f"User {discord_username} tried to delete his database but it does NOT existed.")
                await interaction.followup.send(f"Hmm, there was nothing to delete. It seems we need to create new memories with one another! I can't wait to speak with you {discord_username}!")
            else:
                print(f"Deleted user {discord_username} history.")
                await interaction.followup.send("I deleted your chat history from my database. I hope this was just to start fresh and not because you were mad at me *smile*", file=discord.File('pictures/smile.gif'))
                
            cursor.commit()
            cursor.close()
            
        
        except Exception as e: 
            print(e)
            await interaction.followup.send("Oh, something crushed. Need to look at my logs *looking*", file=discord.File('pictures/shock_2.gif'))

if __name__ == "__main__":
    #connect_to_azuredb_fn("User: What's your name?", "Oh? My name is in the title you dummy! I'm Shiro *smile*")
    
    pass