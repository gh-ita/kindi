import platform
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from transcriptor.audio_transcriptor import transcribe_audio
from voice_agents import task_setting_agent, project_planner_agent
from typing import Optional
from agent_builder import AgentBuilder
from meeting_agent.rag_doc_prep import DocPrep
from meeting_agent.meeting_agent_prompt import meeting_agent_prompt
from meeting_agent.rag_retrieval_tool import RetrieverTool
from g_calendar_api.calendar_api import insert_notes_url, create_doc_for_notes
from dotenv import load_dotenv
from huggingface_hub import login
from os import getenv
from fastapi.middleware.cors import CORSMiddleware
from transcriptor.tts import tts_agent

load_dotenv()
#HUGGINGFACEHUB_API_TOKEN
huggingface_api_token = getenv('HUGGINGFACEHUB_API_TOKEN')
login(huggingface_api_token)

app = FastAPI()
origins = [
    "http://localhost:8000",  
    "http://localhost:3000",
    "http://localhost",       
    "http://127.0.0.1",      
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*", "OPTIONS"],  
    allow_headers=["*"],  
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def get_home():
    with open("static/index.html") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.post("/task_setter")
def run_task_setter(
    model: str = "small",
    energy_threshold: int = 1200,
    record_timeout: float = 0,
    phrase_timeout: float = 0.2,
    default_microphone: Optional[str] = None
):
    """
    Endpoint to run the transcriptor and task-setting agent.
    
    Query Parameters:
        - model: The transcription model to use (default: "small").
        - energy_threshold: Energy level for mic detection (default: 1200).
        - record_timeout: Real-time recording duration in seconds (default: 0).
        - phrase_timeout: Timeout for considering new lines in transcription (default: 0.2).
        - default_microphone: Default microphone name for SpeechRecognition (Linux only).
    """
    if 'linux' in platform.system().lower() and default_microphone is None:
        return {"error": "Please specify a default_microphone for Linux systems."}

    transcriptions = transcribe_audio(
        model_name=model,
        energy_threshold=energy_threshold,
        record_timeout=record_timeout,
        phrase_timeout=phrase_timeout,
        mic_name=default_microphone
    )

    result = task_setting_agent.run(transcriptions)
    tts_agent(result)
    return {"output": result}

@app.post("/project_planner")
def run_project_planner(
    model: str = "small",
    energy_threshold: int = 1200,
    record_timeout: float = 0,
    phrase_timeout: float = 0.2,
    default_microphone: Optional[str] = None
):
    """
    Endpoint to run the transcriptor and project planning agent.
    
    Query Parameters:
        - model: The transcription model to use (default: "small").
        - energy_threshold: Energy level for mic detection (default: 1200).
        - record_timeout: Real-time recording duration in seconds (default: 0).
        - phrase_timeout: Timeout for considering new lines in transcription (default: 0.2).
        - default_microphone: Default microphone name for SpeechRecognition (Linux only).
    """
    if 'linux' in platform.system().lower() and default_microphone is None:
        return {"error": "Please specify a default_microphone for Linux systems."}

    transcriptions = transcribe_audio(
        model_name=model,
        energy_threshold=energy_threshold,
        record_timeout=record_timeout,
        phrase_timeout=phrase_timeout,
        mic_name=default_microphone
    )
    """
    transcription_mock = "Hi Kindi, We are launching a new web app aimed at improving productivity for remote workers, 
    the project starts today and its deadline is the 3O'th of January"
    """
    result = project_planner_agent.run(transcriptions)
    tts_agent(result)
    return {"output": result}

@app.post("/meeting_agent")
def run_task_setter(
    model: str = "small",
    energy_threshold: int = 1200,
    record_timeout: float = 0,
    phrase_timeout: float = 0.2,
    default_microphone: Optional[str] = None
):
    """
    Endpoint to run the transcriptor and meeting_agent.
    
    Query Parameters:
        - model: The transcription model to use (default: "small").
        - energy_threshold: Energy level for mic detection (default: 1200).
        - record_timeout: Real-time recording duration in seconds (default: 0).
        - phrase_timeout: Timeout for considering new lines in transcription (default: 0.2).
        - default_microphone: Default microphone name for SpeechRecognition (Linux only).
    """
    """
    if 'linux' in platform.system().lower() and default_microphone is None:
        return {"error": "Please specify a default_microphone for Linux systems."}
    
    transcriptions = transcribe_audio(
        model_name=model,
        energy_threshold=energy_threshold,
        record_timeout=record_timeout,
        phrase_timeout=phrase_timeout,
        mic_name=default_microphone
    )"""
    
    transcription_mock = """Event Title: first meeting
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
        Thank you!"""
    
    meeting = {
            "name": "first meeting",
            "start_date": "2025-01-06T10:00:00",
            "end_date": "2025-01-06T11:00:00"
            }
    doc_prep_instance = DocPrep(meeting)
    docs_processed = doc_prep_instance.prepare_document(transcription_mock)

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
    result = meeting_agent.run(transcription_mock)
    tts_agent(result)
    return {"output": result}