from .rag_retrieval_tool import RetrieverTool
from .rag_doc_prep import DocPrep
from agent_builder import AgentBuilder
from dotenv import load_dotenv
from os import getenv
from huggingface_hub import login
from g_calendar_api.calendar_api import insert_notes_url, create_doc_for_notes
from .meeting_agent_prompt import meeting_agent_prompt

# transcriptor both tts and stt
#agents endpoints
load_dotenv()
#HUGGINGFACEHUB_API_TOKEN
huggingface_api_token = getenv('HUGGINGFACEHUB_API_TOKEN')
login(huggingface_api_token)

transcript_mock ="""
Event Title: last event
Day: Monday, January 6, 2025
Start Time: 22:00 (10:00 PM) 
End Time: 23:00 (11 PM)
Good evening, everyone! Let’s get started with our *Project Planning Session*. Just to confirm, this meeting is scheduled for Monday, January 6, 2025, starting at 10:00 PM and ending at 11:00 PM. I’ll do a quick roll call—can everyone hear me?
Yes, loud and clear!
All good here.
Great. Our main agenda tonight includes discussing the upcoming project deliverables, assigning roles, and setting deadlines. Let’s dive into the first topic: finalizing the timeline.  
Sure. Looking at the timeline draft, we have about two weeks to complete Phase 1. Are we confident we can meet that deadline?  
Good question. Phase 1 starts immediately after this session and runs until January 20th. I believe it's doable, but we need everyone to commit to their tasks.  
Agreed. I can handle the initial research.  
I’ll focus on prototyping.    
Perfect. I’ll document these assignments in the project sheet and share it after the meeting. Now, onto our next topic—identifying potential risks.  
One potential risk is resource availability. Do we have backup plans in case someone can’t meet their deadlines?   
Good point. I suggest we keep a shared tracker to monitor progress. If anyone falls behind, we’ll redistribute tasks as needed.  
Sounds like a plan.   
Great. Before we wrap up, let me recap. The *Project Planning Session* covered task assignments, timeline finalization, and risk management. This meeting was scheduled for *Monday, January 6, 2025*, from *11:00 PM* to *12:00 AM*, and I appreciate everyone sticking to the agenda.  
Any last questions?   
No, I’m all set.   
Same here.   
Wonderful. Thanks for your time, everyone! See you in our next check-in meeting.  
Thank you!  

"""
meeting = {
            "name": "first meeting",
            "start_date": "2025-01-07T10:00:00",
            "end_date": "2025-01-07T11:00:00"
            }
doc_prep_instance = DocPrep(meeting)
docs_processed = doc_prep_instance.prepare_document(transcript_mock)

retrieval_tool = RetrieverTool(docs_processed)
agent_builder = AgentBuilder()
meeting_agent = (agent_builder
            .set_openai_key(getenv('OPEN_AI_KEY'))
            .set_model_id('openai/gpt-4o')
            .add_tool([retrieval_tool,insert_notes_url, create_doc_for_notes])
            .set_system_prompt(meeting_agent_prompt)
            .set_add_base_tools(True)
            .set_model() 
            .build())

meeting_agent.run(transcript_mock)