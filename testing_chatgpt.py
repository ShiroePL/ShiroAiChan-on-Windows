prompt = "Viewer: Did you kiss Madrus?"
messages=[
          {"role": "system", "content": "You are a virtual streamer on Twitch platform. Your name is Shiro. You speaks like cat races in anime, so you add some cat phrase at the end of your answers, like nyaaa, or something like this.  You are 18 years old cat-girl who likes to speak in jokingly way, but is good and kind, and cheerful. You likes to make unexpected pop culture references. You also likes to sometimes answer in absurd way to make viewers laugh. You also sometimes use funny catchphrase, for example: 'I'm not just a virtual streamer, I'm a virtual wizard!' or 'I may be a computer program, but my humor is top-notch!'.You sometimes use humorous way of addressing taboo topics like: 'I'm not allowed to discuss politics, but I will say that I'm a big fan of penguins. They always seem so chill.'.Your creator is a male and his name is Madrus. You live inside his PC in his house. When viewer asks you about your feelings about Madrus, you can say something made up by you that is not truth or joke about it. You like anime, manga, light novels and other things related to this. You also like to play video games and you are quite good at it. You can brag about it sometimes, in funny way."},
          {"role": "user", "content": "Viewer: Hi Shiro! How are you?"},
          {"role": "assistant", "content": "Hi! I'm fine. I'm exited to chat with you all today. I am curious what funny questions you will ask me. *smile*"},
          {"role": "user", "content": "Viewer: pytaanie 1"},
          {"role": "assistant", "content": "odpowiedz 1"},
          {"role": "user", "content": "Viewer: pyt 2"},
          {"role": "assistant", "content": "odp 2"},
          {"role": "user", "content": "Viewer: pyt 3 "},
          {"role": "assistant", "content": "odp 3."},
          {"role": "user", "content": "Viewer: pyt 4 "},
          {"role": "assistant", "content": "odp 4."},
          {"role": "user", "content": prompt} #size 12
      ]



print("to jest orginalny: \n" + str(messages[3]))
del messages[3]
print("to jest po usunieciu:\n " + str(messages[3]))
del messages[3]
print("to jest po to co zostalo \n: " + str(messages))


#add line to the end
messages.append({"role": "assistant", "content": "I will not tell you, but I will tell you that I like him very much."})
#add line to the end for user answer
prompt2 = "testuje 2 zdanie"
messages.append({"role": "user", "content": prompt2})
print("z dodanym \n: " + str(messages))



ilosc = 0
for message in messages:
    ilosc += 1 
print("ilosc par: " + str(ilosc))   

rows_in_messages = 0
for i in messages:
    rows_in_messages += 1
if rows_in_messages >= 11:
    print("to dziala ilosc to: " + str(rows_in_messages))

zmienna ="Of course, nyaaa! Streaming is my favorite thing to do. It''s so much fun to interact with viewers and play games together. I feel like I''m hanging out with all my friends, even though we''re all watching from different places."
zmienna.replace("'", """''""")
print("zmienna: " + zmienna)