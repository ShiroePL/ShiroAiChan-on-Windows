import openai
import requests
import os
import api_keys
# Set up the API key

#give me enviroment variable for open AI i have on system



# Define the prompt
            
prompt = """User: Can you describe yourself? ->"""

def send_to_openai(prompt):
    # Make the API request
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.4
        #top_p = 0.2
    )
    # Get the generated text from the response
    answer = response["choices"][0]["text"]
    return answer


    #nazwa_modelu = "text-curie-001"
    # text-davinci-003
    # text-curie-001
    # text-babbage-001
    # Get the generated text from the response
    # shiro na 60 pytaniach : curie:ft-personal-2023-02-15-05-51-57
    
#print(send_to_openai(prompt))



if __name__ == "__main__":
    pass