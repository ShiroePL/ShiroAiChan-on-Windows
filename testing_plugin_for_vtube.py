import pyaudio
import numpy as np
import time
import requests
import json

# Define the API endpoint for VTube Studio
vtube_url = "ws://localhost:8001"

# Define the mouth shape mapping based on the audio amplitude and frequency
def map_audio_to_mouth_shape(amplitude, frequency):
    # Define the mapping parameters
    min_amplitude = 0
    max_amplitude = 2**16
    min_frequency = 0
    max_frequency = 22050
    min_mouth_shape = 0
    max_mouth_shape = 1
    
    # Map the amplitude and frequency to a mouth shape value
    mouth_shape = (amplitude - min_amplitude) / (max_amplitude - min_amplitude) * \
                  (max_mouth_shape - min_mouth_shape) + min_mouth_shape
    mouth_shape *= np.sin(frequency * np.pi * 2 / max_frequency) * 0.5 + 0.5
    
    return mouth_shape

# Initialize the PyAudio object for audio capture
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

# Connect to VTube Studio and obtain a reference to the active avatar
response = requests.get(vtube_url)
avatar_id = response.json()[0]["avatarId"]

# Loop through audio capture and apply the mouth shape to the avatar
while True:
    # Read a chunk of audio data from the input stream
    data = np.fromstring(stream.read(1024), dtype=np.int16)
    
    # Compute the amplitude and frequency of the audio data
    amplitude = np.abs(data).mean()
    frequency = np.fft.rfftfreq(data.size, 1/44100)[np.argmax(np.abs(np.fft.rfft(data)))]

    # Map the audio data to a mouth shape value
    mouth_shape = map_audio_to_mouth_shape(amplitude, frequency)

    # Send the mouth shape value to VTube Studio
    payload = {
        "avatarId": avatar_id,
        "parameter": "ParamMouthOpenY",
        "value": str(mouth_shape)
    }
    response = requests.post(vtube_url + "/v1/live2d/parameter", data=json.dumps(payload))
    
    # Wait for a short time to avoid overloading the API
    time.sleep(0.01)
