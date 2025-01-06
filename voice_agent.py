from smolagents import CodeAgent, LiteLLMModel, ManagedAgent
from huggingface_hub import login 
from dotenv import load_dotenv
import os
from calendar_api import check_time_availability, add_task
from task_setter_prompt import task_setter_system_prompt

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


task_setting_agent.run("Hello Kindi, I want you to add a washing dishes task starting from 10 am and ending at 11 am to my google calendar")






