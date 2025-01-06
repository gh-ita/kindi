from huggingface_hub import login 
from dotenv import load_dotenv
from smolagents import ManagedAgent, CodeAgent, LiteLLMModel
from os import getenv
from calendar_api import check_time_availability, add_task
from task_setter_prompt import task_setter_system_prompt
from agent_builder import AgentBuilder
from project_planner_prompt import project_planner_prompt
from manager_prompt import manager_agent_prompt

load_dotenv()
#HUGGINGFACEHUB_API_TOKEN
huggingface_api_token = getenv('HUGGINGFACEHUB_API_TOKEN')
login(huggingface_api_token)

#Define the task setting agent
agent_builder = AgentBuilder()
task_setting_agent = (agent_builder
            .set_openai_key(getenv('OPEN_AI_KEY'))
            .set_model_id('openai/gpt-4o')
            .add_tool([check_time_availability, add_task])
            .set_system_prompt(task_setter_system_prompt)
            .set_add_base_tools(True)
            .set_model() 
            .build())

managed_task_setting_agent = ManagedAgent(agent=task_setting_agent,
                                          name="task_setting",
                                          description="Checks the availability of the specified time slot for you.\
                                               If the time slot is available, it proceeds to add the task to Google Calendar; \
                                                   otherwise, notifies the user that the time slot is unavailable. \
                                                       When inserting a task into a specific time slot, \
                                                           give it the relevant query as an argument.")

#Define the project planning agent 
project_planner_agent = (agent_builder
            .set_openai_key(getenv('OPEN_AI_KEY'))
            .set_model_id('openai/gpt-4o')
            .add_tool([])
            .set_system_prompt(project_planner_prompt)
            .set_add_base_tools(True)
            .set_model() 
            .set_managed_agents([managed_task_setting_agent])
            .build())


managed_project_planner_agent=ManagedAgent(agent=project_planner_agent,
                                             name="project_planner",
                                             description="Plans the project for you, if your query contains \
                                                 a project planning task give it your query")
model=LiteLLMModel(model_id='openai/gpt-4o',
                        api_base=None,
                        api_key=getenv('OPEN_AI_KEY'))

manager_agent=CodeAgent(tools=[], model=model, system_prompt=manager_agent_prompt, managed_agents=[managed_task_setting_agent, managed_project_planner_agent])

#manager_agent.run("Hi Kindi, We are launching a new web app aimed at improving productivity for remote workers, the project starts today and its deadline is the 3O'th of January")

project_planner_agent.run("Hi Kindi, We are launching a new web app aimed at improving productivity for remote workers, the project starts today and its deadline is the 3O'th of January")

