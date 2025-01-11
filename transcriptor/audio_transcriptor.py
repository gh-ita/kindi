import argparse
import os, re
import numpy as np
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform


KEYWORD = "kindi"  # Define your keyword


# Function to detect the keyword in transcriptions
def detect_keyword(transcript):
    return KEYWORD.lower() in transcript.lower()


# Function to transcribe audio from a microphone or audio data
def transcribe_audio(model_name="small", energy_threshold=1200, record_timeout=0, phrase_timeout=0.2, mic_name=None):
    # Load the Whisper model
    model_name = model_name + ".en"
    audio_model = whisper.load_model(model_name)

    # Set up the recognizer and microphone
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    recorder.dynamic_energy_threshold = False

    # Setup for microphone input
    if 'linux' in platform:
        if mic_name and mic_name != 'list':
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
        else:
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
    else:
        source = sr.Microphone(sample_rate=16000)

    transcription = ""
    data_queue = Queue()

    def record_callback(_, audio: sr.AudioData):
        # Grab the raw bytes and push them into the thread-safe queue
        data = audio.get_raw_data()
        data_queue.put(data)

    # Adjust for ambient noise and start listening in the background
    with source:
        recorder.adjust_for_ambient_noise(source)
    stop_listening = recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Recording started... Say the keyword to stop.")

    phrase_time = None
    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                phrase_time = now

                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()


                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0


                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

  
                print(f"Transcription: {text}")
                if phrase_complete:
                    transcription += text
                else:
                    if transcription:
                        transcription += text
                    else:
                        transcription += text
                if re.search(r'\bokay\b', text, re.IGNORECASE):
                    print("\nKeyword detected. Stopping transcription.")
                    stop_listening(wait_for_stop=False)  
                    break

            else:
                sleep(0.05)

        except KeyboardInterrupt:
            print("\nManual interruption. Stopping transcription.")
            stop_listening(wait_for_stop=False)  
            break
    return transcription


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--energy_threshold", default=1200, help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=0, help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=0.2, help="How much empty space between recordings before we consider it a new line in the transcription.", type=float)

    if 'linux' in platform:
        parser.add_argument("--default_microphone", default=None, help="Default microphone name for SpeechRecognition.", type=str)

    args = parser.parse_args()

    mic_name = getattr(args, 'default_microphone', None)

    transcriptions = transcribe_audio(
        model_name=args.model,
        energy_threshold=args.energy_threshold,
        record_timeout=args.record_timeout,
        phrase_timeout=args.phrase_timeout,
        mic_name=mic_name
    )
    print("Final Transcription:", transcriptions)


if __name__ == "__main__":
    main()
