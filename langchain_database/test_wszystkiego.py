from datetime import datetime
from .chatgpt_calendar_prompts import CalendarAssistant
from . import calendar_api_test as cal

def add_event_from_shiro(query:str):
    """Adds event to calendar from shiro gui 
    returns:  answer, prompt_tokens, completion_tokens, total_tokens, |summary, description, dtstart, dtend| in formatted_query_to_calendar"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
    #print(current_time)
    query = f"{query}. today is : {current_time}"

    #print(query)
        #send query to chatgpt and get response in correct format
    calendar_assistant = CalendarAssistant(model="gpt-3.5-turbo")
    # print(assistant.chatgpt_calendar_planer("Add a meeting to my calendar next Monday at 10 AM"))
    answer, prompt_tokens, completion_tokens, total_tokens = calendar_assistant.chatgpt_calendar_planer(query)

        # add event to calendar using api
    summary, description, dtstart, dtend = cal.add_event_to_calendar(answer)

    formatted_query_to_calendar = f"\nsummary: {summary} \ndescription: {description} \ndate: {dtstart} \nend_date: {dtend}"

    return answer, prompt_tokens, completion_tokens, total_tokens, formatted_query_to_calendar


def retrieve_plans_for_days(query:str):
    """Adds event to calendar from shiro's gui.
    This function first calls chatgpt to extract info from answer then calls calendar api to get schedule for specified days 
    returns:  answer, prompt_tokens, completion_tokens, total_tokens"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
    #print(current_time)
    query = f"{query}. today is : {current_time}"

    #print(query)
        #send query to chatgpt and get response in correct format
    calendar_assistant = CalendarAssistant(model="gpt-4")
    answer, prompt_tokens, completion_tokens, total_tokens = calendar_assistant.chatgpt_calendar_schedule(query)
        # add event to calendar using api
    formatted_result = cal.get_schedule_for_day(answer)

    

    return formatted_result, prompt_tokens, completion_tokens, total_tokens


if __name__ == "__main__":
    pass