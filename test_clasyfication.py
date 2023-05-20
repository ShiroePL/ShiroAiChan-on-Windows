# Note: you need to be using OpenAI Python v0.27.0 for the code below to work

import openai
def send_to_openai():
  #modify messages, delete pair if size is too big
  messages = [
          {"role": "system", "content": "You are ai program that classifies sentences to their categories."},
          {"role": "user", "content": "Viewer: i have a job for you. I will give you some sentence, and i would like you to determine in what category this sentance can be added. categories are:'maps, search, wikipedia, email, song, database' Remember this and wait for my next prompt. Then answer me in one word of correct category. are you ready? yes/no"},
          {"role": "assistant", "content": "Yes, i'm ready."},
          {"role": "user", "content": "i want to update my anime list"},
          {"role": "assistant", "content": "Category: Database"},
          {"role": "user", "content": "send message to tom"},
          {"role": "assistant", "content": "Category: Email"},
          {"role": "user", "content": "who is protagonist of ascendance of a bookworm?"},
          {"role": "assistant", "content": "Category: Search"},
          {"role": "user", "content": "population of Warsaw"},
          {"role": "assistant", "content": "Category: Wikipedia"},
          {"role": "user", "content": "when next episode of birdie golf is aired?"},
          ]
  
  #send to openai and get answer
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    #model= "gpt-4",
    messages=messages,
    temperature = 0.6
  )
  #print("full: " + str(completion))

  answer = completion.choices[0].message.content
  prompt_tokens = completion.usage.prompt_tokens
  completion_tokens = completion.usage.completion_tokens
  total_tokens = completion.usage.total_tokens

  return answer, prompt_tokens, completion_tokens, total_tokens

#prompt = "Viewer: Did you kiss Madrus?"
        #completion_tokens = result[2] or _,_,completion_tokens,_ = result if i would like ot take only one


if __name__ == "__main__":
    answer, prompt_tokens, completion_tokens, total_tokens = send_to_openai()
    print("answer: " + answer)
    print("prompt_tokens: " + str(prompt_tokens))
    print("completion_tokens: " + str(completion_tokens))
    print("total_tokens: " + str(total_tokens))
    pass
    
