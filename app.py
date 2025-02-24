import streamlit as st
import os
import tempfile
import asyncio
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

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

st.set_page_config(page_title="AI Video Editor", layout="wide")
st.markdown(
    """
    <style>
    .stTitle { color: #FF4B4B; text-align: center; font-size: 40px; font-weight: bold; }
    .stButton button { background-color: #FF4B4B; color: white; font-size: 18px; border-radius: 10px; }
    .stProgress > div > div { background-color: #FF4B4B; }
    .css-1aumxhk { color: #FF4B4B; font-size: 20px; font-weight: bold; }
    .sidebar-text { font-size: 16px; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎬 AI Video Editor 🚀")
st.markdown("<p class='stTitle'>Automate video editing with AI-powered enhancements!</p>", unsafe_allow_html=True)

uploaded_video = st.file_uploader("📂 **Upload your video**", type=["mp4", "mov", "avi"])

if uploaded_video:
    st.video(uploaded_video)

    with tempfile.NamedTemporaryFile(delete=False) as temp_video:
        temp_video.write(uploaded_video.read())
        input_video = temp_video.name

    st.success("✅ Video uploaded successfully!")

    trim_option = st.radio("✂️ **Trim Video?**", ("No", "Yes"))
    start_time, end_time = None, None
    if trim_option == "Yes":
        start_time = st.text_input("⏱ **Start Time** (seconds or HH:MM:SS):")
        end_time = st.text_input("⏱ **End Time** (seconds or HH:MM:SS):")

    if st.button("🚀 **Start Processing**"):
        try:
            with st.spinner("⏳ **Trimming Video...**"):
                if trim_option == "Yes" and start_time and end_time:
                    trimmed_output = 'trimmed_output_video.mp4'
                    trim_video_original_start_to_end(input_video, trimmed_output, start_time, end_time)
                    input_video = trimmed_output

            with st.spinner("🎧 **Extracting Audio...**"):
                audio_file = convert_video_to_audio(input_video)

            with st.spinner("📜 **Transcribing & Removing Fillers...**"):
                transcribed_text, segments = transcription_of_audio(audio_file)
                filler_words = extract_filler_words(transcribed_text)
                silence_ranges = detect_silence_ranges(audio_file)
                filler_ranges = identify_filler_ranges(segments, filler_words)
                all_trim_ranges = combine_silence_and_fillers(silence_ranges, filler_ranges)
                keep_ranges = get_keep_ranges(all_trim_ranges, audio_file)
                cleaned_audio = remove_silence_and_fillers(audio_file, all_trim_ranges)

            with st.spinner("✂️ **Trimming Silence & Fillers from Video...**"):
                output_video = "output.mp4"
                trim_video(input_video, output_video, keep_ranges)

            with st.spinner("🎭 **Tracking Faces & Speech...**"):
                audio_file, audio_clip = extract_audio(output_video)
                speech_times = detect_speech(audio_file)
                face_tracked_output = "face_tracked_output.mp4"
                process_video(output_video, face_tracked_output, speech_times)

            with st.spinner("🎼 **Merging Cleaned Audio...**"):
                merge_audio("temp_video.mp4", audio_clip, face_tracked_output)
                os.remove("temp_video.mp4")

            with st.spinner("💬 **Generating Subtitles...**"):
                word_subtitles = transcribe_with_word_timestamps(face_tracked_output)
                subtitled_output = "subtitled_output.mp4"
                overlay_live_subtitles(face_tracked_output, word_subtitles, subtitled_output)

            with st.spinner("🖼 **Extracting Keywords & Overlaying Images...**"):
                transcription_text, transcription_segments = transcription_of_audio(subtitled_output)
                keywords = extract_keywords(transcription_text)
                image_paths = download_images(keywords)
                final_output = "final_output.mp4"
                keyword_timestamps = get_keyword_timestamps(transcription_segments, keywords)
                add_images_to_video(subtitled_output, keyword_timestamps, image_paths, final_output)

            st.success("🎉 **Processing Complete! Watch your final video:**")
            video_clip = VideoFileClip(final_output)
            st.video(video_clip.reader.filename)

        except Exception as e:
            st.error(f"❌ Error: {e}")

st.sidebar.header("📌 About this Project")
st.sidebar.markdown(
    """
    <p class='sidebar-text'>
    🎞 **AI-Powered Video Editing**: Remove silence, detect faces, add subtitles, and overlay images automatically.<br>
    🔥 **Fast & Efficient**: Processes your videos seamlessly with AI enhancements.<br>
    🚀 **Built with Python & Streamlit**.
    </p>
    """,
    unsafe_allow_html=True
)
