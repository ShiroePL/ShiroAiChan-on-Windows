import discord
import chatgpt_api
import connect_to_azuredb
import play_audio as play_audio
from better_profanity import profanity
from db_config import conn

async def handle_openai_response_text(interaction, question):
        
    
    async with interaction.channel.typing():
            #check user nick and create table for him if doesn't exist in Azure DB
        discord_username = f"{interaction.user.name}#{interaction.user.discriminator}"
        print("---------------------------------")
        connect_to_azuredb.check_user_in_database(discord_username) #check if user is in database and create table for him/her if not
        messages = connect_to_azuredb.retrieve_chat_history_from_database(discord_username)    
           # Defer the response to let Discord know that the bot is still working
        await interaction.response.defer()       
        try:
            
            if profanity.contains_profanity(question) == False: # if false in question then generate answer
                question_to_db = f"{discord_username}: " + question  #for Azure DB   
                question = f"{discord_username}: " + question #changing to format for open AI

                    #add question line to messages list
                messages.append({"role": "user", "content": question})
                    # send to open ai for answer
                answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages)

                if profanity.contains_profanity(answer) == False: # if false in answer then send the response to the user.               
                    await interaction.followup.send(answer)
                        #add answer line to messages list
                    messages.append({"role": "assistant", "content": answer})
                        #send to Azure DB
                    connect_to_azuredb.insert_message_to_database(discord_username, question, answer, messages) #insert to Azure DB to user table    
                    connect_to_azuredb.connect_to_azuredb_fn(question_to_db, answer) #to general table with all  questions and answers
                    connect_to_azuredb.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                    print("---------------------------------")
                else: # if true in answer then censor and send
                    censored = profanity.censor(answer)
                    connect_to_azuredb.insert_message_to_database(discord_username, question, censored, messages)
                    connect_to_azuredb.connect_to_azuredb_fn(question_to_db, censored)
                    connect_to_azuredb.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens)
                    await interaction.followup.send("Hmm, my answer contains some censored words so I will not say it aloud. *writing on paper*: \n" + censored)
                    print("---------------------------------")
            else:
                await interaction.followup.send("Please don't use bad words in questions! I can't answer to that.", file=discord.File('pictures/shock_2.gif'))
                print("---------------------------------")
        except Exception as e: 
            print(e)
            print("---------------------------------")
            await interaction.followup.send("Oh, something crushed. Need to look at my logs *looking*", file=discord.File('pictures/shock_2.gif'))