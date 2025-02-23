import streamlit as st
import os
import tempfile
import shutil
import uuid
from datetime import datetime
from moviepy.editor import VideoFileClip
from Scripts.Convert_to_Audio import convert_video_to_audio
from Scripts.Transcription_script import transcription_of_audio, extract_filler_words
from Scripts.Silence_and_fillers_removal import detect_silence_ranges, identify_filler_ranges, combine_silence_and_fillers
from Scripts.Cleaned_audio_script import remove_silence_and_fillers
from Scripts.Output_fillers_and_silence_removed import get_keep_ranges, trim_video
from Scripts.Trims_Video import trim_video_original_start_to_end
from Scripts.Face_Tracking import extract_audio, detect_speech, process_video
from Scripts.Merge_Audio import merge_audio
from Scripts.Generate_Subtitles import transcribe_with_word_timestamps
from Scripts.Overlay_Subtitles import overlay_live_subtitles
from Scripts.Keyword_Extraction import extract_keywords
from Scripts.Image_Downloader import download_images
from Scripts.Overlay_Images import add_images_to_video, get_keyword_timestamps

FINAL_OUTPUTS_DIR = "final_outputs"
os.makedirs(FINAL_OUTPUTS_DIR, exist_ok=True)

def main():
    st.title("🎬 AI Video Editor")
    st.write("This app trims videos, removes silence, fillers, and adds live subtitles with relevant images.")

    # Upload Video
    uploaded_video = st.file_uploader("📤 Upload a video file", type=["mp4", "mov", "avi"])
    
    if uploaded_video:
        st.video(uploaded_video)
        
        session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        session_dir = os.path.join("processed_videos", session_id)
        os.makedirs(session_dir, exist_ok=True)

        input_video_path = os.path.join(session_dir, uploaded_video.name)
        with open(input_video_path, "wb") as f:
            f.write(uploaded_video.read())

        st.success(f"✅ Video uploaded successfully! (Session: {session_id})")

        # Trimming options
        trim_option = st.radio("✂️ Do you want to trim the video?", ("No", "Yes"))
        if trim_option == "Yes":
            start_time = st.text_input("Enter start time (seconds or HH:MM:SS):")
            end_time = st.text_input("Enter end time (seconds or HH:MM:SS):")
        
        if st.button("🚀 Process Video"):
            with st.spinner("⏳ Processing video... Please wait!"):
                try:
                    progress_bar = st.progress(0)

                    # Trim video
                    st.write("🔄 Step 1: Trimming video (if selected)...")
                    if trim_option == "Yes" and start_time and end_time:
                        trimmed_video_path = os.path.join(session_dir, "./trimmed_video.mp4")
                        trim_video_original_start_to_end(input_video_path, trimmed_video_path, start_time, end_time)
                        input_video_path = trimmed_video_path
                    progress_bar.progress(10)

                    # Convert to audio
                    st.write("🎵 Step 2: Extracting audio...")
                    audio_file = os.path.join(session_dir, "audio.wav")
                    convert_video_to_audio(input_video_path, audio_file)
                    progress_bar.progress(20)

                    # Transcription and silence/filler removal
                    st.write("📝 Step 3: Transcribing audio...")
                    transcribed_text, segments = transcription_of_audio(audio_file)
                    filler_words = extract_filler_words(transcribed_text)
                    progress_bar.progress(30)

                    st.write("🤐 Step 4: Detecting silences and fillers...")
                    silence_ranges = detect_silence_ranges(audio_file)
                    filler_ranges = identify_filler_ranges(segments, filler_words)
                    all_trim_ranges = combine_silence_and_fillers(silence_ranges, filler_ranges)
                    keep_ranges = get_keep_ranges(all_trim_ranges, audio_file)
                    cleaned_audio_path = os.path.join(session_dir, "cleaned_audio.wav")
                    remove_silence_and_fillers(audio_file, all_trim_ranges, cleaned_audio_path)
                    output_video_path = os.path.join(session_dir, "processed_video.mp4")
                    trim_video(input_video_path, output_video_path, keep_ranges)
                    progress_bar.progress(50)

                    # Face tracking and speech detection
                    st.write("🕵️ Step 5: Face tracking & speech detection...")
                    extracted_audio, audio_clip = extract_audio(output_video_path)
                    speech_times = detect_speech(extracted_audio)
                    face_tracked_video_path = os.path.join(session_dir, "face_tracked_video.mp4")
                    process_video(output_video_path, face_tracked_video_path, speech_times)
                    progress_bar.progress(60)

                    # Merge audio
                    st.write("🎶 Step 6: Merging audio...")
                    merge_audio(face_tracked_video_path, audio_clip)
                    progress_bar.progress(70)

                    # Add subtitles
                    st.write("🔠 Step 7: Adding subtitles...")
                    word_subtitles = transcribe_with_word_timestamps(face_tracked_video_path)
                    subtitled_video_path = os.path.join(session_dir, "subtitled_video.mp4")
                    overlay_live_subtitles(face_tracked_video_path, word_subtitles, subtitled_video_path)
                    progress_bar.progress(80)

                    # Keyword extraction and image overlay
                    st.write("🔍 Step 8: Extracting keywords and overlaying images...")
                    transcription_text, transcription_segments = transcription_of_audio(subtitled_video_path)
                    keywords = extract_keywords(transcription_text)
                    image_paths = download_images(keywords)
                    final_output_path = os.path.join(FINAL_OUTPUTS_DIR, f"final_{session_id}.mp4")
                    keyword_timestamps = get_keyword_timestamps(transcription_segments, keywords)
                    add_images_to_video(subtitled_video_path, keyword_timestamps, image_paths, final_output_path)
                    progress_bar.progress(100)

                    st.success("🎉 Video processing complete!")
                    st.video(final_output_path)

                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # About section
    st.sidebar.header("📌 About this project")
    st.sidebar.write("""
    - **AI Video Editor**: Automatically trims, processes, and enhances videos.
    - **Features**: Silence & filler removal, face tracking, subtitle addition, and keyword-based image overlays.
    - Built using **Streamlit** and **Python video processing libraries**.
    """)

if __name__ == "__main__":
    main()
