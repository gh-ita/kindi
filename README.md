# kindi
Kindi, voice agent.
The project has three agents :
- task setter agent : it sets the task prompted by the user to their google calendar, the user has to specify the name, start time and end time of the task.
- project planning agent : it plans the project, generate tasks and their deadlines then add each task to the user's google calendar
- meeting agent : this agent takes a record of the user's meetings and generates notes, stores them in a google drive file, and appends its url to the google calendar's meeting event.

To run the project :
- install the requirements in the requirements file by running from the main directory 'kindi' : pip install -r requirements.txt (would be better to install the requirements in a virtual env)
- set the environment variables values in the .env file :
HUGGINGFACEHUB_API_TOKEN = ####You need to create an account in hugging face and get a key###
OPEN_AI_KEY = ####Your openai api key#####
- for the tts you need to install FFmpeg here's the link to do so:
https://ffmpeg.org/download.html#build-windows 
- For the google api key you will have to create a google api key, activate the google calendar and drive services, upload the credentials file, then generate the tokens.json file by running the calendar_api script in the g_calendar_api package, then copy the token from the token.json file and paste in the token variable defined in each method inside the calendar_api script
- run the audio_transcriptor script in the transcriptor package to load the whisper model
- run uvicorn main:app --reload to launch the app




