import openai



template = """
        I will give you sentance about adding something to calendar along with current timestamp(example: 2023-07-04 16:11:15.296367+00:00). I want you to extract date that this event will happen and what it is about.
        I want you to give me answer in that EXACT FORMAT: summary: {summary}, description: {description} date: {date}, end_date: {end_date}
        Information about summary: Summary of the event.
        Information about description: Description of the event. Here I want you to write what is the event about. Put here all informations that was given in question. If there are no informations about event, just put "no-info".
        Some information about date: date is in format YYYY,MM,DD,HH,MM,SS
        Information about end_date: this you will need to calculate by yourself. If event is like appointment just make it 1 hour after start date. If specified in question, then do as it says.
        GIVE ME ONLY INFORMATION WHAT I GAVE YOU IN FINAL ANSWER FORMAT, NOTHING MORE.
        Begin!
        Question: remember that friday next week i will be going on vacations, flying to tokyo. plane is at 8:00. vacations will last 5 days. i will be returning at 15:00  2023-07-04 16:13:25.931285+00:00
        Answer:"""

template2 = """
        Use the following structure:
Task: (here comes the task for ChatGPT)
Instructions: (numbered instructions for ChatGPT)

Question: Please write me a tiktok video script which is going to be viral and generates a lot of views
        Answer:"""


answer = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant that do exactly what is it instructed to do. Complete the objective as best you can."},
        {"role": "user", "content": template2}
    ]
)
print(answer)