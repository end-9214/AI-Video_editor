from Convert_to_Audio import convert_video_to_audio
from Transcription_script import transcription_of_audio, extract_filler_words
from Silence_and_fillers_removal import detect_silence_ranges, identify_filler_ranges, combine_silence_and_fillers
from Cleaned_audio_script import remove_silence_and_fillers
from Output_fillers_and_silence_removed import get_keep_ranges, trim_video
from Trims_Video import trim_video_original_start_to_end

input_video = input("Enter the file name or path : ")
output_video = "output.mp4"

choice = int(input("Do you want to trim the video? : 1 [yes], 2 [no] : "))
if choice == 1:
    start_time = input("Enter the start time you want in seconds or HH:MM:SS : ")
    end_time = input("Enter the end time you want in seconds or HH:MM:SS : ")
    trimmed_output = 'trimmed_output_video.mp4'
    trim_video_original_start_to_end(input_video, trimmed_output, start_time, end_time)
    input_video = trimmed_output


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

print("Process Complete!")
