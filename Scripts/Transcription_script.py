import os
import json
from groq import Groq
import time
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def transcription_of_audio(audio_file_path, retries=3):
    client = Groq(api_key=GROQ_API_KEY)
    
    for attempt in range(retries):
        try:
            with open(audio_file_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                )
            return transcription.text, transcription.segments
        except Exception as e:
            print(f"Transcription error (Attempt {attempt+1}): {e}")
            time.sleep(2**attempt)

    return None, None

def extract_filler_words(transcribed_text):
    client = Groq(api_key=GROQ_API_KEY)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant analyzing a transcript. Your task is to identify and return only the filler words or unnecessary phrases that can be removed without altering the core meaning of the text. Respond exclusively in a JSON format with a single key: 'filler_words'."
            },
            {
                "role": "user",
                "content": transcribed_text
            }
        ],
        temperature=0.7,
        max_completion_tokens=512,
        top_p=1,
        response_format={"type": "json_object"},
    )

    response_content = completion.choices[0].message.content
    filler_words_dict = json.loads(response_content)
    return filler_words_dict.get("filler_words", [])
