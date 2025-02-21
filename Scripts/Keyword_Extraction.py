import os
import json
from groq import Groq

def extract_keywords(transcribed_text):
    """Extracts keywords from transcriptions using Groq."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "Extract important keywords from the text."},
                  {"role": "user", "content": transcribed_text}],
        temperature=1,
        max_completion_tokens=1024,
        response_format={"type": "json_object"},
    )

    response_text = completion.choices[0].message.content
    return json.loads(response_text).get("image_keyword", [])
