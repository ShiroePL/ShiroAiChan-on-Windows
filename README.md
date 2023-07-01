# 1. ShiroAi-chan and her friend Kiki-chan
![Screenshot](pictures/shiro_black_github.png)
![Screenshot](pictures/kiki_chan.png)


### My attempt to create my anime waifu assistant that can write and speak in cute voice.

### Description:
My personal Ai assistant ShiroAi-chan. I wanted to create AI girl from a long time and now with really cheap and powerful model like [ChatGPT API] it's possible for anyone.

### Her personality
* She is virtual cat-girl that likes anime, manga, light novels and games. (I wrote it for my preferences, but it can be changed easily). I am using tables as her 'personalities' for example, 'normal' is just her basic character description, but 'programmer' is her when she is in coding mode. Then she can help me with coding or I can just converse with her and she know what I am talking about.

### GUI
![Screenshot](pictures/gui.png)

## What she can do?
### 1. Writing
* She uses [ChatGPT API] to generate responses as AI neko girl.


### 2. Her memory :heart_eyes:
* She uses MariaDB to store her memories. She can remember up to 4 last questions, more is too 
* Vector database is in ChromaDB. It can store pdf's etc. It uses Huggingface Embeddings so it is free. GPU for adding to database, and then CPU for embedding questions.
* Every 'persona' setting has its own table in database and can reset it with button.
  
### 3. Voice :microphone:
*  Using Microsoft [Azure TTS], she can speak in cute voice.
*  If she has too long answer, with button you can skip her talking.

### 4. Communication with her :speech_balloon:
* I am using open source Whisper Model from OpenAI to transcribe audio from microphone to text.
* Of corse, it's possible to just write in input and sent it to her.

### 5. AI functions:
* She uses langchain Agent to choose what Tool use.
  * Tools for now are: 
    * show last 10 anime/manga list from Anilist for user. (also there are buttons for it)
    * you can tell her to update episodes/chapters, and she will send API to Anilist and update it for you :heart_eyes:
    * search vector database
  * to use tools, you can just start question with 'agent mode' or 'agent:' or check agent mode check.

### 6. Other functions:
* She has checkbox for random questions. If checked, she will use random timer and will be asking you questions to initialize conversation.

### 7. Vtube Stuido (her look)
* for now she can connect to Vtube Studio, and play animation. (but it is WIP, for now I tested with button that it works)
### Instructions for me:



#### To do but small steps:
* #### Anilist
  * Maybe add pop up window that will show with better formatting the list

* #### Memory
  * need to add tool for adding short info to vector DB
* #### Look :star_struck:
  * I need to record some animations in [Vtube studio].
  * [to do next] And i will need to use some combination of Sentiment Analysis and key words combinations to get needed info to play appropriate animation. Azure or something.

* #### Uncategorize
  * when i interrupt her TTS , picture with text bubble will appear near her head and say: Why are you interrupting me? :< 
  
## Links 

[ChatGPT API] : https://openai.com/blog/introducing-chatgpt-and-whisper-apis



[Azure TTS] : https://azure.microsoft.com/en-us/products/cognitive-services/text-to-speech/



[ChatGPT API]: https://openai.com/blog/introducing-chatgpt-and-whisper-apis
[Azure TTS]: https://azure.microsoft.com/en-us/products/cognitive-services/text-to-speech/

