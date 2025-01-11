import platform
from fastapi import FastAPI, Request,Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from transcriptor.audio_transcriptor import transcribe_audio
from typing import Optional
from agent_builder import AgentBuilder
from meeting_agent.rag_doc_prep import DocPrep
from meeting_agent.meeting_agent_prompt import meeting_agent_prompt
from meeting_agent.rag_retrieval_tool import PineconeRetrieverTool
from dotenv import load_dotenv
from huggingface_hub import login
from os import getenv
from fastapi.middleware.cors import CORSMiddleware
from transcriptor.tts import tts_agent
import urllib.parse
from pinecone.grpc import PineconeGRPC as Pinecone
from helpers import *
from meeting_recap_agent.retrieval_tool import PineconeRecapRetrieverTool



#Loading env variables
load_dotenv()
#HUGGINGFACEHUB_API_TOKEN
HUGGINGFACEHUB_API_TOKEN = getenv('HUGGINGFACEHUB_API_TOKEN')
#Google client ID
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT_URI = getenv("REDIRECT_URI")
SCOPE = ["https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/calendar.events"]
scope_param = " ".join(SCOPE)
task_setter_agent_instance = None 
project_planning_agent_instance = None   
meeting_recap_agent_instance = None
google_calendar_service = None  
google_drive_service = None
current_meeting = None 
meeting_recap_agent_instance = None
agent_builder = AgentBuilder()
pinecone_api_key = getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
login(HUGGINGFACEHUB_API_TOKEN)
app = FastAPI()

#CORS authorization
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
#Mounting the statis files 
app.mount("/static", StaticFiles(directory="static"), name="static")


#Landing page
@app.get("/")
def get_landing_page():
    with open("static/index.html") as f:
        content = f.read()
    return HTMLResponse(content=content)

#Login page 
@app.get("/login")
def get_login_page():
    with open('static/login.html') as f :
        content = f.read()
    return HTMLResponse(content=content)

#The OAuth api
@app.get("/generate-oauth-url")
def generate_oauth_url():
    oauth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        + urllib.parse.urlencode({
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": scope_param,
            "access_type": "offline",
            "prompt": "consent",
        })
    )
    return JSONResponse({"url": oauth_url})

 
#Home page
@app.get("/kindi", response_class=HTMLResponse)
async def get_home(request: Request):
    global task_setter_agent_instance, project_planning_agent_instance, google_calendar_service, google_drive_service
    code = request.query_params.get("code")
    if code:
        with open("static/kindi.html") as f:
            content = f.read()
        code = request.query_params.get("code")
        token_json = exchange_code_for_token(code)
        task_setter_agent_instance = initialize_task_agent(token_json)
        project_planning_agent_instance = initialize_project_agent(token_json)
        google_drive_service = initialize_google_drive(token_json)
        google_calendar_service = initialize_google_calendar(token_json)
        return HTMLResponse(content=content)
        
    else:
        return HTMLResponse(content=f"<h1>OAuth flow uncomplete!</p>")
    
    


#The task setter agent endpoint
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
    result = task_setter_agent_instance.run(transcriptions)
    tts_agent(result)
    return {"output": result}

#The project planner agent endpoint 
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
    result = project_planning_agent_instance.run(transcriptions)
    tts_agent(result)
    return {"output": result}


#The meeting agent API endpoint
@app.post("/meeting_agent")
def run_task_setter(
    meeting: Optional[str] = Query("default_meeting", description="The name of the meeting (Pinecone namespace)"),
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
    ### gadi hadi
    embeddings = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[doc_processed['text'] for doc_processed  in docs_processed],
    parameters={"input_type": "passage", "truncate": "END"}
    )
    doc_prep_instance.add_to_vector_store(docs_processed, embeddings)
    retrieval_tool = PineconeRetrieverTool(meeting["name"],"multilingual-e5-large",docs_processed, pc)
    if google_drive_service and google_calendar_service:
        agent_builder = AgentBuilder()
        meeting_agent = (agent_builder
                    .set_openai_key(getenv('OPEN_AI_KEY'))
                    .set_model_id('openai/gpt-4o')
                    .add_tool([retrieval_tool,google_drive_service, google_calendar_service])
                    .set_system_prompt(meeting_agent_prompt)
                    .set_add_base_tools(True)
                    .set_model() 
                    .build())
        result = meeting_agent.run(transcription_mock)
        tts_agent(result)
        return {"output": result}
    
    
#Meeting recap
@app.post('/meeting_recap')
def run_meeting_recap_agent(
    meeting: Optional[str] = Query("default_meeting", description="The name of the meeting (Pinecone namespace)"),
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
    global current_meeting, meeting_recap_agent_instance
    
    # Check if the meeting name has changed
    if meeting != current_meeting or meeting_recap_agent_instance is None:
        current_meeting = meeting
        retrieval_tool =  PineconeRecapRetrieverTool(current_meeting["name"],"multilingual-e5-large" ,pc)
        agent_builder = AgentBuilder()
        meeting_recap_agent_instance = (
            agent_builder
            .set_openai_key(getenv('OPEN_AI_KEY'))
            .set_model_id('openai/gpt-4o')
            .add_tool([retrieval_tool])
            .set_system_prompt(meeting_agent_prompt)
            .set_add_base_tools(True)
            .set_model()
            .build()
        )
    if 'linux' in platform.system().lower() and default_microphone is None:
        return {"error": "Please specify a default_microphone for Linux systems."}

    transcriptions = transcribe_audio(
        model_name=model,
        energy_threshold=energy_threshold,
        record_timeout=record_timeout,
        phrase_timeout=phrase_timeout,
        mic_name=default_microphone
    )
    """meeting = {
            "name": "first meeting",
            "start_date": "2025-01-06T10:00:00",
            "end_date": "2025-01-06T11:00:00"
"""
    result = meeting_recap_agent_instance.run(transcriptions)
    tts_agent(result)
    return {"output": result}

