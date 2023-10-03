import requests
from .. import api_keys

# token = api_keys.token
# server_ip = api_keys.server_ip

def room_temp():
    token = api_keys.token
    server_ip = api_keys.server_ip
    url = f"http://{server_ip}:8123/api/states/sensor.living_room_temperature_2"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        temperature = response.json()['state']
        print(f"The living room temperature is {temperature}°C")
    else:
        print(f"Failed to get temperature: {response.content}")
    return temperature
#room_temp(token, server_ip)