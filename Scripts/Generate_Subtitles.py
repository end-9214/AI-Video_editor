import whisper
import torch

def transcribe_with_word_timestamps(audio_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("large").to(device)
    result = model.transcribe(audio_path, word_timestamps=True)

    word_segments = []
    for segment in result["segments"]:
        for word in segment["words"]:
            word_segments.append((word["start"], word["end"], word["word"]))
    transcribed_text = result["text"]

    return word_segments, transcribed_text
