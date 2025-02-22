import whisper
import torch

def transcribe_with_word_timestamps(audio_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model = whisper.load_model("large").to(device)


    result = model.transcribe(audio_path, word_timestamps=True)


    word_segments = []
    for segment in result["segments"]:
        for word in segment["words"]:
            word_segments.append((word["start"], word["end"], word["word"]))

    return word_segments