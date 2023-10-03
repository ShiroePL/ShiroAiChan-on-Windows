import json
import threading
import time
import websocket

class VTubeStudioAPI:
    def __init__(self):
        self.ws = websocket.WebSocketApp(
            "ws://localhost:8001",
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error,
        )
        self.ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={"ping_interval": 20})
        self.ws_thread.start()
        time.sleep(1)  # Give the connection some time to establish

    def on_open(self, ws):
        print("WebSocket connection opened")
        self.authenticate()

    def on_message(self, ws, message):
        print("Received message:", message)

    def on_close(self, ws):
        print("Connection closed")

    def close(self):
        self.ws.close()
        self.ws_thread.join()

    def on_error(self, ws, error):
        print("Error:", error)

    def authenticate(self):
        self.ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": "Shiro chan",
                "pluginDeveloper": "Madrus",
                "authenticationToken": "c7c5296f2450ca697726e8e05b257586ee7f550671c4b0b5ee2ed7c7ad4c6cbc" #this need to be changed to variable
            }
        }))

    def play_animation(self, hotkeyID):
        self.ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": hotkeyID
            }
        }))