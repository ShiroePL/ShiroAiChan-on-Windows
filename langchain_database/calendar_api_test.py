from datetime import datetime, timedelta
import caldav
from icalendar import Calendar, Event
from . import private_variables #this works if function is used from shiros functions
#import private_variables # this works if function is used from this file
from datetime import datetime
from pytz import utc
import re


# replace these with your Nextcloud server details
url = private_variables.nextcloud_url
username = private_variables.username
password = private_variables.password


def add_event_to_calendar(answer):
    # initialize the client
    client = caldav.DAVClient(url=url, username=username, password=password)
    # get the principal
    principal = client.principal()

    

    summary_match = re.search(r'(?<=summary: ).*?(?=description:|$)', answer, re.DOTALL)
    summary = summary_match.group().strip() if summary_match else "None"
    summary = re.sub(r'[.,]$', '', summary) # deletes . or , at the end of string

    description_match = re.search(r'(?<=description: ).*?(?=date:|$)', answer, re.DOTALL)
    description = description_match.group().strip() if description_match else "None"
    description = re.sub(r'[.,]$', '', description) # deletes . or , at the end of string

    dtstart_match = re.search(r'(?<=date: ).*?(?=end_date:|$)', answer, re.DOTALL)
    if dtstart_match:
        dtstart_str = dtstart_match.group().strip()
        dtstart_str = dtstart_str.rstrip(',')  # remove comma, if present
        dtstart = datetime.strptime(dtstart_str, '%Y-%m-%d %H:%M:%S')

    dtend_match = re.search(r'(?<=end_date: ).*', answer, re.DOTALL)
    if dtend_match:
        dtend_str = dtend_match.group().strip()
        dtend_str = dtend_str.rstrip(',')  # remove comma, if present
        dtend = datetime.strptime(dtend_str, '%Y-%m-%d %H:%M:%S')


    print("-----formated event info-----")
    print ("summary: " + summary)
    print ("description: " + description)
    print ("dtstart: " + str(dtstart))
    print ("dtend: " + str(dtend))
    print("-----------------------------")

    # get the calendars and select the first one
    calendars = principal.calendars()
    if calendars:

        calendar = calendars[0]
            # create an event
        event = Calendar()
        event.add('prodid', '-//My calendar product//mxm.dk//')
        event.add('version', '2.0')
        
        event_event = Event()
            # Assign the parsed values to the event
        event_event.add('summary', summary)
        event_event.add('dtstart', dtstart)
        event_event.add('dtend', dtend)
        #if description != "None":
        event_event.add('description', description)
        event_event.add('dtstamp', datetime.now(utc)) 
        event.add_component(event_event)
        
        # add the event to the calendar
        calendar.save_event(event.to_ical())
        print("event added to calendar")
    return description, summary, dtstart, dtend

def get_schedule_for_day(answer_from_chatgpt):
    """get schedule for specified days"""


    #extract dates from answer
    def extract_dates(text):
        matches = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        return [datetime.strptime(match, '%Y-%m-%d') for match in matches]
    
    dates = extract_dates(answer_from_chatgpt)

    # Accessing dates
    start_date = dates[0]
    end_date = dates[1]

    print("Start Date:", start_date)
    print("End Date:", end_date)



    # initialize the client
    client = caldav.DAVClient(url=url, username=username, password=password)

    # get the principal
    principal = client.principal()

    # get the calendars and select the first one
    calendars = principal.calendars()
    if calendars:
        calendar = calendars[0]
        #testing
        # specify the date you are interested in
        # date = datetime(2023, 7, 11)
        # end_date = datetime(2023, 7, 16)
        # get the events for that date
        results = calendar.date_search(start=start_date, end=end_date + timedelta(days=1)) #timedelta is because without it, it gives one day less, it does not include the end date
        formatted_result = ""
        # print event details
        for event in results:
            ical_event = Calendar.from_ical(event.data)
            for component in ical_event.walk():
                if component.name == "VEVENT":
                    formatted_result += "Summary: " + str(component.get('summary')) + "\n"
                    formatted_result += "Starts at: " + str(component.get('dtstart').dt) + "\n"
                    formatted_result += "Ends at: " + str(component.get('dtend').dt) + "\n"
                    formatted_result += "Description: " + str(component.get('description')) + "\n\n"

        
        
    return formatted_result        

if __name__ == "__main__":
    # start_date = datetime(2023, 7, 11)
    # end_date = datetime(2023, 7, 12)
    # get_shedule_for_day(start_date, end_date)
    pass