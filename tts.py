from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from transformers import tool

@tool
def tts_agent(text: str) -> None:
    """
    Convert text to speech and play it in real-time.

    This function takes a text string as input, converts it to speech using the Google Text-to-Speech (gTTS) library, 
    and plays the generated audio in real-time without saving it to a file. The audio is processed in memory 
    using a BytesIO buffer and played using the pydub library.

    Args:
        text: The text string to be converted to speech and played.

    Returns:
        None
    """
    # Convert text to speech
    tts = gTTS(text=text, lang='en')
    # Save the audio to a BytesIO buffer
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    # Load the buffer with pydub
    audio = AudioSegment.from_file(audio_buffer, format="mp3")

    # Play the audio
    play(audio)





