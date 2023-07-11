import openai


def chatgpt_calendar_planer(query):
    template = f"""
            I will give you sentence about adding something to calendar along with current timestamp(example: 2023-07-04 16:11:15.296367+00:00). I want you to extract date that this event will happen and what it is about.
            I want you to give me answer in that EXACT FORMAT: summary: summary, description: description date: date, end_date: end_date
            Information about summary: Summary of the event.
            Information about description: Here put description of event, information's not included in summary.
            Some information about date: date is in EXACT FORMAT: YYYY-MM-DD HH:MM:SS ALWAYS INCLUDE HOUR, MINUTES AND SECONDS. If there is no information about time, just put 00:00:00.
            Information about end_date: this you will need to calculate by yourself. If specified in question, then do as it says.If event is like appointment just make it all day, from 00:00:00 to next day 00:00:00 
            GIVE ME ONLY INFORMATION WHAT I GAVE YOU IN FINAL ANSWER FORMAT, NOTHING MORE.
            Begin!
            Question: {query}
            Answer:"""


    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    #temperature = 1,
    messages=[
            {"role": "system", "content": "You are a helpful assistant that do exactly what is it instructed to do. Complete the objective as best you can. Follow the exact format that is given to you."},
            {"role": "user", "content": template}
        ]
    )
    answer = completion.choices[0].message.content
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    total_tokens = completion.usage.total_tokens

    return answer, prompt_tokens, completion_tokens, total_tokens


def chatgpt_calendar_schedule(query):
    template = f"""
            I will give you a sentence about retrieving a schedule from a calendar for a specific date, along with a current timestamp (example: 2023-07-04 16:11:15.296367+00:00). I want you to extract the date for which the schedule needs to be retrieved.
            I want you to give me the answer in this EXACT FORMAT: date: date
            Information about date: The date is in EXACT FORMAT: YYYY-MM-DD ALWAYS INCLUDE YEAR, MONTH, AND DAY. Do not include the time in this case, as we are interested in the full day schedule.
            GIVE ME ONLY INFORMATION THAT I GAVE YOU IN THE FINAL ANSWER FORMAT, NOTHING MORE.
            Begin!
            Question: {query}
            Answer:"""


    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    #temperature = 1,
    messages=[
            {"role": "system", "content": "You are a helpful assistant that do exactly what is it instructed to do. Complete the objective as best you can. Follow the exact format that is given to you."},
            {"role": "user", "content": template}
        ]
    )
    answer = completion.choices[0].message.content
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    total_tokens = completion.usage.total_tokens

    return answer, prompt_tokens, completion_tokens, total_tokens
  


if __name__ == "__main__":
    pass

# answer, prompt_tokens, completion_tokens, total_tokens = chatgpt_calendar_planer("remember that 13 July  i will be going on vacations for 5 days long, flying to tokyo .plane is at 8:00. today is : 2023-07-04 16:11:15.296367+00:00")
# print(answer)
# print(prompt_tokens)
# print(completion_tokens)
# print(total_tokens)