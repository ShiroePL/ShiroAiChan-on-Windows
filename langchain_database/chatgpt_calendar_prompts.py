import openai

class CalendarAssistant:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    def _run_chatgpt(self, template):
        completion = openai.ChatCompletion.create(
            model=self.model,
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

    def chatgpt_calendar_planer(self, query):
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
        template_refined = f"""I will provide a sentence about adding an event to a calendar, along with a current timestamp (e.g., 2023-07-04 16:11:15.296367+00:00). Your task is to extract the date of the event and its details.

            Please use the EXACT following format for the answer:
            summary: [summary], description: [description], date: [date], end_date: [end_date]

            Summary: This is the main event title.
            Description: Any additional details about the event not covered in the summary.
            Date: Use the format YYYY-MM-DD HH:MM:SS. If no time is specified, default to 00:00:00.
            End_date: If provided in the question, use that. For appointments, use an all-day event, starting at 00:00:00 and ending the next day at 00:00:00.
            Ensure your answer only includes the requested details in the specified format.

            Begin!
            Question: {query}
            Answer:"""
        return self._run_chatgpt(template)

    def chatgpt_calendar_schedule(self, query):
        template = f"""
            I will give you a sentence about retrieving a schedule from a calendar for a specific date, along with a current timestamp (example: 2023-07-04 16:11:15.296367+00:00). I want you to extract start day and end day for which the schedule needs to be retrieved. When I mention "this week", consider it as the period from the current date to the end of the week (Sunday).
            I want you to give me the answer in this EXACT FORMAT: start_date: start_date, end_date: end_date.
            Information about start_date: The start_date in EXACT FORMAT: YYYY-MM-DD ALWAYS INCLUDE YEAR, MONTH, AND DAY. Do not include the time in this case, as we are interested in the full day schedule.
            Information about end_date: The end_date in EXACT FORMAT: YYYY-MM-DD ALWAYS INCLUDE YEAR, MONTH, AND DAY. End date is last day for what user requested. 'this week' means last day is SUNDAY. Do not include the time in this case. 'TODAY' means end_date is same as start_date.
            GIVE ME ONLY INFORMATION THAT I GAVE YOU IN THE FINAL ANSWER FORMAT, NOTHING MORE.
            Begin!
            Question: {query}
            Answer:"""
        return self._run_chatgpt(template)

if __name__ == "__main__":
    pass
    # assistant = CalendarAssistant(model="gpt-4")
    # print(assistant.chatgpt_calendar_planer("Add a meeting to my calendar next Monday at 10 AM"))
