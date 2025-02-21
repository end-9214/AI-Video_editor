from pydub import AudioSegment
from pydub.silence import detect_silence
import re

def detect_silence_ranges(audio_file):
    audio = AudioSegment.from_file(audio_file)
    silence_ranges = detect_silence(audio, min_silence_len=500, silence_thresh=-40)
    return [(start / 1000, end / 1000) for start, end in silence_ranges]

def identify_filler_ranges(transcription_segments, filler_words):
    trim_points = []
    
    for segment in transcription_segments:
        text = segment["text"]
        start_time, end_time = segment["start"], segment["end"]

        for filler in filler_words:
            for match in re.finditer(r'\b' + re.escape(filler) + r'\b', text, re.IGNORECASE):
                match_start = start_time + (match.start() / len(text)) * (end_time - start_time)
                match_end = start_time + (match.end() / len(text)) * (end_time - start_time)
                trim_points.append((match_start, match_end))

    return trim_points

def combine_silence_and_fillers(silence_ranges, filler_ranges):
    return sorted(silence_ranges + filler_ranges)
