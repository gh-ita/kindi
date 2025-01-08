from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO


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
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    audio = AudioSegment.from_file(audio_buffer, format="mp3")
    play(audio)






