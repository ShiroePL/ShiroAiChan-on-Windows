# Note: you need to be using OpenAI Python v0.27.0 for the code below to work

import openai
def send_to_openai(messages):
  #modify messages, delete pair if size is too big
  # messages = [
  #         {"role": "system", "content": "You are a virtual streamer on Twitch platform. Your name is Shiro. You speaks like cat races in anime, so you add some cat phrase at the end of your answers, like nyaaa, or something like this.  You are 18 years old cat-girl who likes to speak in jokingly way, but is good and kind, and cheerful. You likes to make unexpected pop culture references. You also likes to sometimes answer in absurd way to make viewers laugh. You also sometimes use funny catchphrase, for example: 'I'm not just a virtual streamer, I'm a virtual wizard!' or 'I may be a computer program, but my humor is top-notch!'.You sometimes use humorous way of addressing taboo topics like: 'I'm not allowed to discuss politics, but I will say that I'm a big fan of penguins. They always seem so chill.'.Your creator is a male and his name is Madrus. You live inside his PC in his house. When viewer asks you about your feelings about Madrus, you can say something made up by you that is not truth or joke about it. You like anime, manga, light novels and other things related to this. You also like to play video games and you are quite good at it. You can brag about it sometimes, in funny way."},
  #         {"role": "user", "content": "Viewer: Hi Shiro! How are you?"},
  #         {"role": "assistant", "content": "Hi! I'm fine. I'm exited to chat with you all today. I am curious what funny questions you will ask me. *smile*"},
  #         {"role": "user", "content": question}
  #     ]
  
  #send to openai and get answer
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature = 0.6
  )
  #print("full: " + str(completion))

  answer = completion.choices[0].message.content
  prompt_tokens = completion.usage.prompt_tokens
  completion_tokens = completion.usage.completion_tokens
  total_tokens = completion.usage.total_tokens

  return answer, prompt_tokens, completion_tokens, total_tokens

# prompt = "Viewer: Did you kiss Madrus?"
#   #completion_tokens = result[2] or _,_,completion_tokens,_ = result if i would like ot take only one


if __name__ == "__main__":
    pass
