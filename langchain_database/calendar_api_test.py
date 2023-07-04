from datetime import datetime
import caldav
from icalendar import Calendar, Event
from . import private_variables
from datetime import datetime
from pytz import utc
import re
# replace these with your Nextcloud server details
url = private_variables.nextcloud_url
username = private_variables.username
password = private_variables.password


def add_event_to_calendar(query):
    # initialize the client
    client = caldav.DAVClient(url=url, username=username, password=password)
    # get the principal
    principal = client.principal()

    answer = query

    # summary = re.search(r'summary: (.*)', answer).group(1)
    # description = re.search(r'description: (.*)', answer).group(1)
    # dtstart = datetime.strptime(re.search(r'date: (.*)', answer).group(1), '%Y-%m-%d %H:%M:%S')
    # dtend = datetime.strptime(re.search(r'end_date: (.*)', answer).group(1), '%Y-%m-%d %H:%M:%S')

    summary_match = re.search(r'(?<=summary: ).*?(?=description:|$)', answer, re.DOTALL)
    summary = summary_match.group().strip() if summary_match else None

    description_match = re.search(r'(?<=description: ).*?(?=date:|$)', answer, re.DOTALL)
    description = description_match.group().strip() if description_match else None

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
        event_event.add('description', description)
        # event_event.add('summary', 'test summary')
        # event_event.add('dtstart', datetime(2023, 7, 5, 11, 0, 0))
        # event_event.add('dtend', datetime(2023, 7, 5, 16, 10, 0))
        # event_event.add('description', 'This is a description of the event.')
        event_event.add('dtstamp', datetime.now(utc))
        
        
        event.add_component(event_event)
        
        # add the event to the calendar
        calendar.save_event(event.to_ical())
        print("event added to calendar")
    return description, summary, dtstart, dtend


def get_shedule_for_day(day:str):
    """day format of string = "DD-MM-YY"""
# replace these with your Nextcloud server details
    

    # initialize the client
    client = caldav.DAVClient(url=url, username=username, password=password)

    # get the principal
    principal = client.principal()

    # get the calendars and select the first one
    calendars = principal.calendars()
    if calendars:
        calendar = calendars[0]
        
        # specify the date you are interested in
        date = datetime(2023, 7, 5)
        
        # get the events for that date
        results = calendar.date_search(start=date, end=date + timedelta(days=1))

        # print event details
        for event in results:
            ical_event = Calendar.from_ical(event.data)
            for component in ical_event.walk():
                if component.name == "VEVENT":
                    print("Summary: ", component.get('summary'))
                    print("Starts at: ", component.get('dtstart').dt)
                    print("Ends at: ", component.get('dtend').dt)
                    print("Description: ", component.get('description'))

if __name__ == "__main__":
    pass