from playsound import playsound


def play_audio_fn():
    try:
        playsound('./kiki_hub/response.wav')
        print("Playing voice")
    except:
        print("Error or ended reading audio.")

play_audio_fn()