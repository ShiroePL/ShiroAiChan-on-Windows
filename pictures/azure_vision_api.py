import os
import requests
from PIL import Image
import io

# Replace with your own API key and endpoint
subscription_key = "5e1b4e95033147ddadccf022095c292e"
endpoint = "https://bezplatna.cognitiveservices.azure.com/"

# Define the OCR API url
ocr_url = endpoint + "/vision/v3.1/ocr"

# Set the image file path
image_path = "test_screenshot.png"

# Open the image
with open(image_path, "rb") as image_file:
    image_data = image_file.read()

# Set the headers and parameters for the API request
headers = {
    "Ocp-Apim-Subscription-Key": subscription_key,
    "Content-Type": "application/octet-stream"
}
params = {"language": "en", "detectOrientation": "true"}

# Make the API request
response = requests.post(ocr_url, headers=headers, params=params, data=image_data)

# Raise an exception if the request failed
response.raise_for_status()

# Parse the OCR result
ocr_result = response.json()

# Extract text from the OCR result
extracted_text = ""
for region in ocr_result["regions"]:
    for line in region["lines"]:
        for word in line["words"]:
            extracted_text += word["text"] + " "
        extracted_text += "\n"

# Print the extracted text
print("Extracted Text:")
print(extracted_text)