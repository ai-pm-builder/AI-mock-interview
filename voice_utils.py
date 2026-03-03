import os
from gtts import gTTS
import tempfile
import streamlit as st
import io

def text_to_speech(text: str):
    """Converts text to speech and returns the audio file path or bytes."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang='en')
        tts.save(fp.name)
        return fp.name

def play_audio(audio_path_or_bytes):
    """Plays audio in Streamlit."""
    if isinstance(audio_path_or_bytes, str):
        with open(audio_path_or_bytes, "rb") as f:
            audio_bytes = f.read()
    else:
        audio_bytes = audio_path_or_bytes
    
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

def transcribe_audio(audio_bytes, model_name="gemini-2.0-flash"):
    """Uses Gemini to transcribe audio bytes to text."""
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name)
    
    # Create the audio part
    audio_part = {
        "mime_type": "audio/wav",
        "data": audio_bytes
    }
    
    response = model.generate_content([
        "Please transcribe this audio accurately. If it's silent, return an empty string. Only return the transcription.",
        audio_part
    ])
    
    return response.text.strip()
