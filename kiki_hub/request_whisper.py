import requests
import base64
import time


def transcribe_audio_question():
    start_time = time.time()
    # Load audio file as base64 encoded string
    with open("./kiki_hub/recording.wav", "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode("utf-8")

    response = requests.post("http://127.0.0.1:7860/run/predict", json={
        "data": [
            "transcribe",
            "gpu",
            "en",
            "base.en",
            {"name": "recording.wav", "data": f"data:audio/wav;base64,{audio_data}"},
            {"name": "recording.wav", "data": f"data:audio/wav;base64,{audio_data}"}
        ]
    }).json()

    question = response["data"][0]
    print("-------") 
    print("text from audio question: " + question)
    end_time = time.time()
    print("time elapsed on transcription: " + str(end_time - start_time))
    print("-------")
    return question

#give me __main
if __name__ == "__main__":
    pass
    #transcribe_audio_question()

#MODELS:
# tiny
# base
# small
# medium