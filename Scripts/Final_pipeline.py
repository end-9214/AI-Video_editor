from Face_Tracking import extract_audio, detect_speech, process_video
from Merge_Audio import merge_audio
from Generate_Subtitles import transcribe_with_word_timestamps
from Overlay_Subtitles import overlay_live_subtitles
from Keyword_Extraction import extract_keywords
from Image_Downloader import download_images
from Overlay_Images import add_images_to_video,get_keyword_timestamps
from Transcription_script import transcription_of_audio

import os

input_video = "output.mp4"
audio_file, audio_clip = extract_audio(input_video)
speech_times = detect_speech(audio_file)

face_tracked_output = "face_tracked_output.mp4"
process_video(input_video, face_tracked_output, speech_times)

merge_audio("temp_video.mp4", audio_clip, face_tracked_output)
os.remove("temp_video.mp4")

word_subtitles = transcribe_with_word_timestamps(face_tracked_output)
subtitled_output = "subtitled_output.mp4"
overlay_live_subtitles(face_tracked_output, word_subtitles, subtitled_output)

transcription_text, transcripton_segments = transcription_of_audio(subtitled_output)

keywords = extract_keywords(transcription_text)
image_paths = download_images(keywords)

final_output = "final_output.mp4"
keyword_timestamps = get_keyword_timestamps(transcripton_segments, keywords)
add_images_to_video(subtitled_output, keyword_timestamps, image_paths, final_output)

print("Final video processing complete!")
