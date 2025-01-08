from smolagents import LiteLLMModel, CodeAgent
from huggingface_hub import login
from dotenv import load_dotenv
from os import getenv

# Load environment variables
load_dotenv()
# Log into Huggingface Hub 
huggingface_key = getenv('HUGGINGFACEHUB_API_TOKEN')
login(huggingface_key)


class Agent:
    def __init__(self, openai_key=None, model_id=None, tools=None, system_prompt=None, add_base_tools=True, model=None,managed_agents = None):
        self.openai_key = openai_key
        self.model_id = model_id
        self.tools = tools if tools is not None else []
        self.system_prompt = system_prompt
        self.add_base_tools = add_base_tools
        self.model = model  
        self.managed_agents = managed_agents

    def __str__(self):
        return (f"Agent(openai_key={self.openai_key}, model_id={self.model_id}, "
                f"tools={self.tools}, system_prompt={self.system_prompt}, "
                f"add_base_tools={self.add_base_tools}, model={self.model})")

class AgentBuilder:
    def __init__(self):
        self.openai_key = None
        self.model_id = None
        self.tools = []
        self.system_prompt = None
        self.add_base_tools = True
        self.model = None
        self.managed_agents = None 

    def set_openai_key(self, key):
        self.openai_key = key
        return self

    def set_model_id(self, model_id):
        self.model_id = model_id
        return self

    def add_tool(self, tools):
        self.tools = tools
        return self

    def set_system_prompt(self, prompt):
        self.system_prompt = prompt
        return self

    def set_add_base_tools(self, value):
        self.add_base_tools = value
        return self
    
    def set_model(self):
        if not (self.openai_key and self.model_id):
            raise ValueError("OpenAI key and model ID must be set before creating the model.")
        
        self.model = LiteLLMModel(model_id=self.model_id,
                                  api_base=None,
                                  api_key=self.openai_key)
        return self
    
    def set_managed_agents(self, value):
        self.managed_agents = value
        return self


    def build(self):
        return CodeAgent(
            tools=self.tools,
            model=self.model,
            system_prompt=self.system_prompt,
            add_base_tools=self.add_base_tools,
            managed_agents = self.managed_agents
        )



        
