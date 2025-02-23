import os
from Convert_to_Audio import convert_video_to_audio
from Transcription_script import transcription_of_audio, extract_filler_words
from Silence_and_fillers_removal import detect_silence_ranges, identify_filler_ranges, combine_silence_and_fillers
from Cleaned_audio_script import remove_silence_and_fillers
from Output_fillers_and_silence_removed import get_keep_ranges, trim_video
from Trims_Video import trim_video_original_start_to_end
from Face_Tracking import extract_audio, detect_speech, process_video
from Merge_Audio import merge_audio
from Generate_Subtitles import transcribe_with_word_timestamps
from Overlay_Subtitles import overlay_live_subtitles
from Keyword_Extraction import extract_keywords
from Image_Downloader import download_images
from Overlay_Images import add_images_to_video, get_keyword_timestamps

def main():
    try:
        input_video = input("Enter the file name or path: ")
        if not os.path.exists(input_video):
            raise FileNotFoundError("Input video file not found.")
        
        output_video = "output.mp4"
        
        choice = int(input("Do you want to trim the video? : 1 [yes], 2 [no] : "))
        if choice == 1:
            start_time = input("Enter the start time you want in seconds or HH:MM:SS : ")
            end_time = input("Enter the end time you want in seconds or HH:MM:SS : ")
            trimmed_output = 'trimmed_output_video.mp4'
            trim_video_original_start_to_end(input_video, trimmed_output, start_time, end_time)
            input_video = trimmed_output

        audio_file = convert_video_to_audio(input_video)
        if not audio_file:
            raise Exception("Audio extraction failed.")
        
        transcribed_text, segments = transcription_of_audio(audio_file)
        if transcribed_text and segments:
            filler_words = extract_filler_words(transcribed_text)
            silence_ranges = detect_silence_ranges(audio_file)
            filler_ranges = identify_filler_ranges(segments, filler_words)
            all_trim_ranges = combine_silence_and_fillers(silence_ranges, filler_ranges)
            keep_ranges = get_keep_ranges(all_trim_ranges, audio_file)
            cleaned_audio = remove_silence_and_fillers(audio_file, all_trim_ranges)
            trim_video(input_video, output_video, keep_ranges)
        else:
            raise Exception("Transcription failed.")
        
        audio_file, audio_clip = extract_audio(output_video)
        if not audio_file:
            raise Exception("Face tracking audio extraction failed.")
        speech_times = detect_speech(audio_file)
        face_tracked_output = "face_tracked_output.mp4"
        process_video(output_video, face_tracked_output, speech_times)
        
        merge_audio("temp_video.mp4", audio_clip, face_tracked_output)
        os.remove("temp_video.mp4")
        
        word_subtitles = transcribe_with_word_timestamps(face_tracked_output)
        subtitled_output = "subtitled_output.mp4"
        overlay_live_subtitles(face_tracked_output, word_subtitles, subtitled_output)
        
        transcription_text, transcription_segments = transcription_of_audio(subtitled_output)
        if not transcription_text:
            raise Exception("Keyword extraction transcription failed.")
        
        keywords = extract_keywords(transcription_text)
        if not keywords:
            raise Exception("Keyword extraction failed.")
        
        image_paths = download_images(keywords)
        if not image_paths:
            raise Exception("Image downloading failed.")
        
        final_output = "final_output.mp4"
        keyword_timestamps = get_keyword_timestamps(transcription_segments, keywords)
        add_images_to_video(subtitled_output, keyword_timestamps, image_paths, final_output)
        
        print("Final video processing complete!")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
