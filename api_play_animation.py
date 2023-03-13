import json
from websocket import create_connection
# Import the module from the folder
import subprocess
def play_animation_fn():
    
	ws = create_connection("ws://localhost:8001")

	# open session
	# ws.send(json.dumps({
	# 	"apiName": "VTubeStudioPublicAPI",
	# 	"apiVersion": "1.0",
	# 	"requestID": "SomeID",
	# 	"messageType": "AuthenticationRequest",
	# 	"data": {
	# 		"pluginName": "Shiro chan",
	# 		"pluginDeveloper": "Madrus",
	# 		"authenticationToken":"c7c5296f2450ca697726e8e05b257586ee7f550671c4b0b5ee2ed7c7ad4c6cbc"
	# 	}
	# }))

	# result = ws.recv()
	# print(result)

	# Start the animation
	ws.send(json.dumps({
		"apiName": "VTubeStudioPublicAPI",
		"apiVersion": "1.0",
		"requestID": "SomeID",
		"messageType": "HotkeyTriggerRequest",
		"data": {
			"hotkeyID": "introduce"
		}
	}))

# 	ws.send(json.dumps({
# 	"apiName": "VTubeStudioPublicAPI",
# 	"apiVersion": "1.0",
# 	"requestID": "SomeID",
# 	"messageType": "AuthenticationTokenRequest",
# 	"data": {
# 		"pluginName": "Shiro chan",
# 		"pluginDeveloper": "Madrus"
# 	}
# }))

	result = ws.recv()
	print(result)
	# file_name = "resultt.json"
	# with open(file_name, "w") as file:
	# 	file.write(result)
	ws.close()
	
play_animation_fn()
# subprocess.Popen(["python", "play_audio.py"])