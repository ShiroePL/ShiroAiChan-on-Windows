import requests
import json
from home_assistant.api_keys import weather_api
#D:\111111.PROGRAMOWANIE\AI W PYTHONIE\shiro_on_streamlit
def current_temperature():
   
    API_KEY = weather_api
    CITY = "Warsaw,PL"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

    # Update the URL to include the API key and the city
    url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY + "&units=metric"

    # Make the HTTP request
    response = requests.get(url)

    # Parse the JSON data
    data = response.json()

    # Check if the API request was successful
    if data["cod"] != "404":
        # Navigate to the temperature data
        temp = data['main']['temp']
        # Display the temperature
        print(f"The current temperature in {CITY} is {temp}°C.")
    else:
        print("City Not Found!")
    return temp


