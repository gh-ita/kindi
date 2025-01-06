import platform
import argparse
from audio_transcriptor import transcribe_audio
from voice_agents import task_setting_agent

"""from typing import Union
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}"""
    
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




