from Face_Tracking import extract_audio, detect_speech, process_video
from Merge_Audio import merge_audio
from Keyword_Extraction import extract_keywords
from Image_Downloader import download_images
from Overlay_Images import add_images_to_video

input_video = "output.mp4"
output_video = "face_tracked_output.mp4"

audio_file, audio_clip = extract_audio(input_video)
speech_times = detect_speech(audio_file)
process_video(input_video, output_video, speech_times)
merge_audio("temp_video.mp4", audio_clip, output_video)

keywords = extract_keywords("transcribed text")
image_paths = download_images(keywords)
add_images_to_video(output_video, {}, image_paths, "final_output.mp4")

print("✅ Final processing complete!")
