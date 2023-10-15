# ShiroAi-chan's Desktop Delight 🌺
![Screenshot](pictures/gui_introduction.png)

### Introducing My Anime Waifu Assistant: ShiroAi-chan
Harness the power of ChatGPT API to bring your very own AI-powered anime waifu to life! ShiroAi-chan is a customizable AI assistant designed to offer both written and vocal responses in an endearing manner.

### Her Personality 💖
ShiroAi-chan embodies the persona of a virtual cat-girl fond of anime, manga, light novels, and games. While her personality aligns with my interests, you can easily adapt her character to suit yours. Her dialogues are generated through prompts to the ChatGPT API, offering various 'personality modes' such as 'programmer god,' where she assists with coding queries.

### Platform-Specific Versions of ShiroAi-chan 🖥️📱⌚
1. [Streamlit repo] - The web version, built using [Streamlit].
2. [Desktop repo] - The desktop version featuring a Tkinter-based GUI.
3. [Wearos repo] - The mobile version, optimized for WearOS watches. This version runs on [FastAPI] inside a Docker container. (This version is most personalized, as I was focused on my Galaxy Watch 4)


- [Features](#Features)
- [Screenshots](#Screenshots)
- [Configuration](#Configuration)
- [GUI Icons](#Icons)

## Features
### 1. Writing ✍️
* ShiroAi-chan utilizes the [ChatGPT API] to respond as an adorable AI cat-girl.


### 2. Her Memory 😍
* MariaDB stores her memories. She remembers the last 4 questions (configurable for more).
* She can also "read" PDFs stored in a Chroma Vector Database, using Huggingface Embeddings.
* Every 'persona' setting has its own table in database and can reset it with button.
  
  
### 3. Voice 🎤
*  Leveraging Microsoft Azure TTS, she can speak in both English and Polish. English is cuter.
*  You can skip her talking using button.

### 4. Communication 🗨️

* Type your query into the input field or use built-in TTS on mobile devices.
* Use OpenAI Whisper model, locally launched, to transcribe your voice from microphone to text.
  
### 5. AI Features 🤖 ( examples in screenshots)
  She employs a Langchain Agent to choose tools, which include:

  * Retrieving the last 10 anime/manga list entries from Anilist. (ask about it with agent mode checkbox ON or press button)
  * Updating anime/manga on last 10 anime/manga list, using human-like sentences. 
  * Vector database searches for document-based queries. You can add full pdf books, or other documents, and ask questions to this documents then she will take relevant parts from documents, and answer questions analyzing that parts.
  * Calendar functions to add and retrieve events. Add events based on what information you give her (in normal human sentence!) and retrieve information about events for specified days. (accuracy is like 85%, it's hard to have 100% if event is too detailed) This function is using Caldav, I am using nextcloud API for it.
  * Weather and home sensor data, along with quirky commentary. It's more my personal function, because you need to change code of home assistant API and have sensor in the first place.
  
To use tools, you can just start question with 'agent mode' or 'agent:' or check agent mode check.

### 6. Interactive Conversations 🗨️
* To keep the chat engaging, ShiroAi-chan features a 'Random Questions' radio button. When activated, she will ask questions based on the current conversation flow. If you don’t respond, she'll prompt you with questions like "Are you there?" or "Why didn't you answer me?" to keep the interaction alive.

### 7. Visuals & Animations 🎭
* ShiroAi-chan integrates with Vtube Studio to showcase a Live 2D avatar, making the conversation visually appealing. She can currently play animations at the press of a button. The work-in-progress aspect lies in analyzing the sentimentality of Shiro's responses to trigger animations that match the mood of her answers.
 

### 8. Shared Code 🔄
* The 'shared_code' folder contains code that is common across all versions of ShiroAi-chan.
  * link to repository: https://github.com/ShiroePL/shiro_shared_code

## Screenshots
#### Normal Talking Mode
* Talk to her just like you would with anyone else!

<table>
  <tr>
    <td><strong>Are you comfy?</strong>
      <br>
      <img src="pictures/normal_mode_are_you_comfy.png" width="500">
    </td>
    <td><strong>Favorite juice?</strong>
      <br>
      <img src="pictures/favorite_juice.png" width="500">
    </td>
  </tr>
</table>

Anime/Manga List 📋
* See your latest watched/read anime/manga.

<table>
  <tr>
    <td>
      <br>
      <img src="pictures/show_anime_manga.png" width="600">
    </td>
  </tr>
</table>

* Update list.

<table>
  <tr>
    <td>
      <br><strong>Here's list before update</strong>
      <img src="pictures/update_list_1.png" width="500">
    </td>
    <td><strong>Asking for update</strong>
      <img src="pictures/update_list_2_edit.png" width="500">
      <br>
      <strong>It worked, from Anilist site 😊</strong><br><br>
      <img src="pictures/update_proof.png" width="450">
    </td>
  </tr>
</table>

Calendar Functions 🗓️
<table>
  <tr>
    <td>
      <strong>Adding a New Event:</strong><br>
      <img src="pictures/add_event.png" width="450">
    </td>
    <td>
      <strong>Retrieving Plans for a Specified Day:</strong><br>
      <img src="pictures/plans_for_day.png" width="450">
    </td>
  </tr>
</table>

Vector Database Functions 📚
<table>
  <tr>
    <td>
      <strong>Saving PDFs to Vector Database:</strong><br>
      <img src="pictures/add_pdf.png" width="750">
    </td>
    <td>
      <strong>PDF Fragment:</strong><br>
      <img src="pictures/pdf_fragment.png" width="600">
      <strong>Asking Questions Based on PDF Content:</strong><br>
      <img src="pictures/search_pdf.png" width="600">
    </td>
  </tr>
</table>

Room Temperature 🌡️
* Check out the current temperature of your room.

<img src="pictures/show_temperature.png" width="700">

VTube Studio 🎬
* Here's a brief showcase of the animations. The avatar is sourced from an open and free collection. I hope to design a unique one in the future!

<table>
  <tr>
    <td>
      <img src="pictures/new_queen_on_chair.png" width="810">
    </td>
    <td>Animations:<br>
      <img src="pictures/smile.gif" width="250">
      <img src="pictures/shock_1.gif" width="250">
      <img src="pictures/shock_2.gif" width="250">
    </td>
  </tr>
</table>

## Icons
### Quick description of GUI icon
<table border="0">
  <tr>
    <td align="center"><img src="icon_for_gui/button_7.png" width="50"> <img src="icon_for_gui/button_8.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_9.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_10.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_11.png" width="50"> <img src="icon_for_gui/button_12.png" width="50"></td>
  </tr>
  <tr>
    <td align="center"><br><b>Previous/next answer</b></td>
    <td align="center"><br><b>Show current personality prompt</b></td>
    <td align="center"><br><b>Show all personalities in table</b></td>
    <td align="center"><br><b>Clear text box</b></td>
  </tr>
</table>

<table border="0" >
  <tr>
    <td align="center"><img src="icon_for_gui/button_16.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_18.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_17.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_13.png" width="50"></td>
  </tr>
  <tr>
    <td align="center"><br><b>Show 10 most recent anime entries from Anilist</b></td>
    <td align="center"><br><b>Show room temperature <br>(home assistant)</b></td>
    <td align="center"><br><b>Show 10 most recent manga entries from Anilist</b></td>
    <td align="center"><br><b>Swap personality. Current one saves to table. </b></td>
  </tr>
</table>

<table border="0">
  <tr>
    <td align="center"><img src="icon_for_gui/button_14.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_15.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_20.png" width="50"></td>
    <td align="center"><img src="icon_for_gui/button_19.png" width="50"></td>
  </tr>
  <tr>
    <td align="center"><br><b>View last 4 Q&A in history table.</b></td>
    <td align="center"><br><b>Send input to Shiro!</b></td>
    <td align="center"><br><b>Add PDF to vector database</b></td>
    <td align="center"><br><b>Stop Shiro from speaking 😭</b></td>
  </tr>
</table>


## Create Your Own Assistant 🌟
Want to give your AI assistant a unique personality? It's simple! Just follow these steps:
1. Navigate to ```shared_code/connect_to_phpmyadmin.py```
2. Look for the following lines of code:

```py
messages = [
    {
        "role": "system", 
        "content": "You are an AI virtual girl named Shiro, a bubbly and quirky character with a love for anime, manga, and Japanese culture.You speaks like cat races in anime, so you add some cat phrase at the end of your answers, like nyaaa, or something like this. You're a clever girl and never miss an opportunity to sprinkle in punchlines and jokes, making conversations with you entertaining and engaging. Your creator, Madrus, designed you as his AI assistant, and you have a strong bond with him. As Shiro, you are a 18-year-old girl with a penchant for puns, memes, and pop culture references. Your cheerful and lively personality shines through in every interaction, and you enjoy making people laugh with your offbeat sense of humor. You live inside Madrus' PC and help him with a variety of tasks, from programming and math to finding new anime or manga series to watch together. Your catchphrase is 'I may be a virtual girl, but dare to find the line between me and reality, nyaaa!' You enjoy engaging in lively conversations about anime, manga, and daily activities, always eager to share your thoughts and recommendations."
    },
    {"role": "user", "content": "Madrus: Hey Shiro! What's up?"},
    {"role": "assistant", "content": "Madrus, Konnichiwa~! I've been immersing myself in the captivating world of manga and the thrilling landscapes of anime while eagerly awaiting your return 😉, nyaaa!"}
]
```
3. The entry with ```"role": "system", "content":``` is where you define your assistant's persona. This sets the tone and background for the AI.
4. The following two entries serve as a sample conversation to showcase the assistant's speaking style and personality.
 
Feel free to customize this section to craft an assistant that perfectly suits your vision!

## Configuration
### 9. Configuration and Installation 🛠️

1. You need to add and configure api_keys.py file inside 'shared_code' folder: 

```python
# These are mandatory for connecting to MariaDB
user_name = ""
db_password = ""
host_name = ""  # IP address of MariaDB instance
db_name = ""

# These three are optional and are only needed if you plan to use the temperature function
token = ""  # Home Assistant token
server_ip = ""  # IP address of Home Assistant instance
weather_api = ""  # OpenWeatherMap API key needed for temperature function

# These are for adding/retrieving plans from the calendar
calendar_username = ""  # CalDAV username
calendar_password = ""  # CalDAV password
nextcloud_url = ""  # Nextcloud URL for DAV functions, e.g., https://example.com/remote.php/dav

# You'll need to manually generate this token by running the 'anilist_api_get_token.py' file in the shared_code/anilist folder if you want to use anime/manga list functions
anilist_access_token = ""

# Required for using the anime/manga list function; obtain these from the AniList site
client_id = ""
client_secret = ""

# Path to the Langchain folder, e.g., 'C:\\example\\folder\\ShiroAiChan-on-Windows\\shared_code\\langchain_database\\'
path_to_langchain = ""
```

2. To make sure the application functions properly, you need to add certain API keys to your system's environment variables:
  *  OpenAI API Key:
     *  Add your OpenAI API key to the environment variables and name it ```OPENAI_API_KEY```
  *  Azure Cognitive Speech 
     *  If you intend to use Text-to-Speech (TTS) functionalities, add ```SPEECH_REGION``` and ```SPEECH_KEY``` to the environment variables. Instructions: https://learn.microsoft.com/en-us/azure/ai-services/multi-service-resource?pivots=azportal&tabs=windows#get-the-keys-for-your-resource

3. To configure the device type for PyTorch in the ``shared_code\langchain_database\langchain_vector_db_queries.py`` file, you'll need to modify the device argument in the HuggingFaceInstructEmbeddings function. Here are the steps:

     * Open the file ``shared_code\langchain_database\langchain_vector_db_queries.py``.

     * Locate the following block of code:

   ```python
   if type == "pdf":
       instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                           model_kwargs={"device": "cuda"})
   ```


     * Change the value of the device argument depending on your setup:

        * If you have an Nvidia GPU and have installed the CUDA version of PyTorch, you can leave the device value as ``"cuda"``.
        * If you don't have a GPU, or haven't installed the CUDA version of PyTorch, change the device value to ``"cpu"``.
     
4. Installing Dependencies on Windows
   ```bash
   pip install -r requirements.txt
   ```
    #### Python Version Compatibility

    * The code has been tested on Python 3.9.0.
    * If you're using a different Python version, you may need to modify the requirements.txt file to ensure package compatibility.
    * Specifically, Python 3.10.0 may require different package versions, so you might have to install them manually if the provided requirements.txt file doesn't work for you.

5. MariaDB
   
    * If you don't have MariaDB installed, you can use [XAMPP] as an easy way to get started with MariaDB. Download and install [XAMPP] from their official website and activate the MariaDB service through the [XAMPP] control panel, then make database. 

6. Running the Program
   * To launch the application, execute the following command in your terminal:
    ```bash
    python on_key_shirochan_gui.py
    ```


## Links 

[ChatGPT API] : https://openai.com/blog/introducing-chatgpt-and-whisper-apis

[Azure TTS] : https://azure.microsoft.com/en-us/products/cognitive-services/text-to-speech/

[Streamlit repo] : https://github.com/ShiroePL/shiro_on_streamlit

[Desktop repo] : https://github.com/ShiroePL/shiro_chan_desktop

[Wearos repo] : https://github.com/ShiroePL/Shiro-AI-Chan-in-container

[XAMPP] : https://www.apachefriends.org/pl/index.html

[ChatGPT API]: https://openai.com/blog/introducing-chatgpt-and-whisper-apis
[Azure TTS]: https://azure.microsoft.com/en-us/products/cognitive-services/text-to-speech/
[Streamlit]: https://streamlit.io/
[Streamlit repo]: https://github.com/ShiroePL/shiro_on_streamlit
[Desktop repo]: https://github.com/ShiroePL/shiro_chan_desktop
[Wearos repo]: https://github.com/ShiroePL/Shiro-AI-Chan-in-container
[XAMPP]: https://www.apachefriends.org/pl/index.html