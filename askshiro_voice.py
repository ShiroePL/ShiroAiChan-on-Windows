import discord
import chatgpt_api
import connect_to_azuredb
import play_audio as play_audio
import request_voice_tts as request_voice
from better_profanity import profanity
import asyncio
import time

async def handle_openai_response_voice(question,interaction):
        #start time
    start_time = time.time()
    user = interaction.user
    discord_username = f"{interaction.user.name}#{interaction.user.discriminator}" 
    print("---------------------------------")
    connect_to_azuredb.check_user_in_database(discord_username) #check if user is in database and create table for him/her if not
    messages = connect_to_azuredb.retrieve_chat_history_from_database(discord_username)           
    try:
        if profanity.contains_profanity(question) == False: # if false in question then generate answer
            
            question_to_db = f"{discord_username}: " + question  #for Azure DB   
            question = f"{discord_username}: " + question #changing to format for open AI
                #add question line to messages list
            messages.append({"role": "user", "content": question})
                # send to open ai for answer
            answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_api.send_to_openai(messages)

            if profanity.contains_profanity(answer) == False: # if false in answer then  
                    #send to azure db
                connect_to_azuredb.insert_message_to_database(discord_username, question, answer, messages) #insert to Azure DB to user table    
                connect_to_azuredb.connect_to_azuredb_fn(question_to_db, answer) #to general table with all  questions and answers
                connect_to_azuredb.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens) #to Azure DB with usage stats
                print("---------------------------------")   
                    #tts request
                request_voice.request_voice_fn(answer) #IT WOULD BE GOOD TO RUN THIS IN SUBPROCES BEFORE DATABASE
                   
                
                
                        # Check if the user is in a voice channel.
                if user.voice is None:
                    await interaction.followup.send("You are not in a voice channel! but here is answer: \n" + answer)
                    return
                    # Connect to the user's voice channel.
                voice_client = await user.voice.channel.connect()
                
                    # Load the audio file and apply volume transformation.
                audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable='C:/ffmpeg/bin/ffmpeg.exe', source='response.wav'), volume=0.5)
                    #stop time
                end_time = time.time()
                print("time for all shiro voice function, remember 2 secounds for kiki and time for transcription: " + str(end_time - start_time))
                    # Play the audio.
                voice_client.play(audio_source)

                while voice_client.is_playing():
                    await asyncio.sleep(1)
                    # Disconnect from the voice channel.
                await voice_client.disconnect()
                #connect_to_azuredb.connect_to_azuredb_fn(question_to_db, answer)
            else:       # if answer contains some censored words
                    #send to azure db   
                censored = profanity.censor(answer)
                connect_to_azuredb.insert_message_to_database(discord_username, question, censored, messages)
                connect_to_azuredb.connect_to_azuredb_fn(question_to_db, censored)
                connect_to_azuredb.send_chatgpt_usage_to_database(prompt_tokens, completion_tokens, total_tokens)
        
        
        
        #else: #NEED TO RECORD ONE TIME AUDIO THAT SHE WILL SAY THAT
            #await interaction.followup.send("Please don't use bad words in questions! I can't answer to that.", file=discord.File('pictures/shock_2.gif'))
    except Exception as e: 
        print(e) # RECORD ONE TO
    