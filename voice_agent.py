from smolagents import CodeAgent, LiteLLMModel, ManagedAgent
from huggingface_hub import login 
from dotenv import load_dotenv
import os
from calendar_api import check_time_availability, add_task
from task_setter_prompt import task_setter_system_prompt
from audio_transcriptor import transcribe_audio
import argparse
from sys import platform

#define tools
#define the prompt 
#use the transcriber twilio 

load_dotenv()
#HUGGINGFACEHUB_API_TOKEN
huggingface_api_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
login(huggingface_api_token)
#OPEN_AI_API_KEY
openai_key = os.getenv('OPEN_AI_KEY')


model_id = 'openai/gpt-4o'
model = LiteLLMModel( model_id = model_id, 
                     api_base = None, 
                     api_key = openai_key )

#Define the task setter slave agent ;p
task_setting_agent = CodeAgent(tools=[check_time_availability, add_task],
                                model=model,
                                system_prompt= task_setter_system_prompt,
                                add_base_tools=True)
#Encapsulate the slave agent ;p in a managed agent object
"""managed_task_setting_agent = ManagedAgent(agent=task_setting_agent,
                                           name="task setter",
                                           description="Checks the availability of the specified time slot for you.\
                                               If the time slot is available, it proceeds to add the task to Google Calendar; \
                                                   otherwise, notifies the user that the time slot is unavailable. \
                                                       When inserting a task into a specific time slot, \
                                                           give it the relevant query as an argument.")

#Define the agent manager or master agent ;p
manager_agent = CodeAgent(tools=[], model=model, managed_agents=[managed_task_setting_agent])"""

#manager_agent.run("Hello Kindi, I want you to add a washing dishes task starting from 10 am and ending at 11 am to my google calendar")


#task_setting_agent.run("Hello Kindi, I want you to add a washing dishes task starting from 10 am and ending at 11 am to my google calendar")


def main():
    # Argument parser for user input (optional)
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--energy_threshold", default=1200, help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=0, help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=0.2, help="How much empty space between recordings before we consider it a new line in the transcription.", type=float)

    # Make `default_microphone` optional
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default=None, help="Default microphone name for SpeechRecognition.", type=str)

    # Parse the arguments
    args = parser.parse_args()

    # Ensure that the default_microphone argument is passed only when it exists
    mic_name = getattr(args, 'default_microphone', None)

    # Call the transcribe_audio function
    transcriptions = transcribe_audio(
        model_name=args.model,
        energy_threshold=args.energy_threshold,
        record_timeout=args.record_timeout,
        phrase_timeout=args.phrase_timeout,
        mic_name=mic_name
    )
    print("Final Transcription:", transcriptions)
    task_setting_agent.run(transcriptions)
    

if __name__ == "__main__":
    main()




