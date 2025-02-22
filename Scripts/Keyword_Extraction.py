import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_keywords(transcribed_text):


    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "you are a image's keyword provider assistent, you whole task is to look into the transcribed text and by understanding the transcribed text you need to look for the important keywords or phrases and give me the 'image_keyword' in JSON such that i can use those keyword to search the web and find images of that. and those keywords should be or phrases should be in the transcribed text."
            },
            {
                "role": "user",
                "content": transcribed_text
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        response_format={"type": "json_object"},
    )

    response_text = completion.choices[0].message.content
    keyword_data = json.loads(response_text)
    return keyword_data.get("image_keyword", [])
