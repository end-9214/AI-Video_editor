import librosa
import numpy as np
import soundfile as sf

def remove_silence_and_fillers(audio_file, trim_ranges):
    y, sr = librosa.load(audio_file, sr=None)

    samples_to_remove = [(int(start * sr), int(end * sr)) for start, end in trim_ranges]

    audio_trimmed = []
    last_end = 0

    for start_sample, end_sample in samples_to_remove:
        audio_trimmed.append(y[last_end:start_sample])
        last_end = end_sample

    audio_trimmed.append(y[last_end:])
    audio_trimmed = np.concatenate(audio_trimmed)
    sf.write("cleaned_audio.mp3", audio_trimmed, sr)

    print("Cleaned audio saved as 'cleaned_audio.mp3'")
    return "cleaned_audio.mp3"
