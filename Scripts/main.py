from Convert_to_Audio import convert_video_to_audio
from Transcription_script import transcription_of_audio, extract_filler_words
from Silence_and_fillers_removal import detect_silence_ranges, identify_filler_ranges, combine_silence_and_fillers
from Cleaned_audio_script import remove_silence_and_fillers
from Output_fillers_and_silence_removed import get_keep_ranges, trim_video

input_video = "input.mp4"
output_video = "output.mp4"

audio_file = convert_video_to_audio(input_video)

if audio_file:
    transcribed_text, segments = transcription_of_audio(audio_file)
    if transcribed_text and segments:
        filler_words = extract_filler_words(transcribed_text)
        silence_ranges = detect_silence_ranges(audio_file)
        filler_ranges = identify_filler_ranges(segments, filler_words)
        all_trim_ranges = combine_silence_and_fillers(silence_ranges, filler_ranges)
        keep_ranges = get_keep_ranges(all_trim_ranges, audio_file)
        cleaned_audio = remove_silence_and_fillers(audio_file, all_trim_ranges)
        trim_video(input_video, output_video, keep_ranges)

print("✅ Process Complete!")
