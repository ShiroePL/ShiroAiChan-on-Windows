from datetime import datetime
from . import chatgpt_calendar_prompts as chatgpt
from . import calendar_api_test as cal

def add_event_from_shiro(query:str):
    """Adds event to calendar from shiro gui 
    returns:  answer, prompt_tokens, completion_tokens, total_tokens, |summary, description, dtstart, dtend| in formatted_query_to_calendar"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
    #print(current_time)
    query = f"{query}. today is : {current_time}"

    #print(query)
        #send query to chatgpt and get response in correct format
    answer, prompt_tokens, completion_tokens, total_tokens = chatgpt.chatgpt_calendar_planer(query)

        # add event to calendar using api
    summary, description, dtstart, dtend = cal.add_event_to_calendar(answer)

    formatted_query_to_calendar = f"\nsummary: {summary} \ndescription: {description} \ndate: {dtstart} \nend_date: {dtend}"

    return answer, prompt_tokens, completion_tokens, total_tokens, formatted_query_to_calendar


def retrieve_plans_for_days(query:str):
    """Adds event to calendar from shiro gui 
    returns:  answer, prompt_tokens, completion_tokens, total_tokens"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
    #print(current_time)
    query = f"{query}. today is : {current_time}"

    #print(query)
        #send query to chatgpt and get response in correct format
    
    answer, prompt_tokens, completion_tokens, total_tokens = chatgpt.chatgpt_calendar_planer(query)
        # add event to calendar using api
    formatted_result = cal.get_schedule_for_day(answer)

    

    return formatted_result, prompt_tokens, completion_tokens, total_tokens


if __name__ == "__main__":
    pass