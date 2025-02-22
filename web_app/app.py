import os
import sys
from flask import Flask, request, redirect, url_for, send_file, render_template, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, set_key

# Load environment variables from .env file
load_dotenv()

# Add the Scripts directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts')))

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

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['PROCESSED_FOLDER']):
    os.makedirs(app.config['PROCESSED_FOLDER'])

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    api_key = request.form.get('api_key')
    if api_key:
        # Save the API key to the .env file
        set_key('.env', 'GROQ_API_KEY', api_key)
        # Reload environment variables
        load_dotenv()
        return redirect(url_for('upload_form'))
    return 'API Key is required!', 400

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return redirect(url_for('process_video', filename=filename))

@app.route('/process/<filename>', methods=['GET', 'POST'])
def process_video(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    trimmed_output = 'trimmed_output_video.mp4'
    output_video = 'output.mp4'
    face_tracked_output = "face_tracked_output.mp4"
    subtitled_output = "subtitled_output.mp4"
    final_output = "final_output.mp4"

    if request.method == 'POST':
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        if start_time and end_time:
            trim_video_original_start_to_end(file_path, trimmed_output, start_time, end_time)
            file_path = trimmed_output

        audio_file = convert_video_to_audio(file_path)
        if audio_file:
            transcribed_text, segments = transcription_of_audio(audio_file)
            if transcribed_text and segments:
                filler_words = extract_filler_words(transcribed_text)
                silence_ranges = detect_silence_ranges(audio_file)
                filler_ranges = identify_filler_ranges(segments, filler_words)
                all_trim_ranges = combine_silence_and_fillers(silence_ranges, filler_ranges)
                keep_ranges = get_keep_ranges(all_trim_ranges, audio_file)
                cleaned_audio = remove_silence_and_fillers(audio_file, all_trim_ranges)
                trim_video(file_path, output_video, keep_ranges)
            
            audio_file, audio_clip = extract_audio(output_video)
            speech_times = detect_speech(audio_file)
            process_video(output_video, face_tracked_output, speech_times)
            merge_audio("temp_video.mp4", audio_clip, face_tracked_output)
            os.remove("temp_video.mp4")
            word_subtitles = transcribe_with_word_timestamps(face_tracked_output)
            overlay_live_subtitles(face_tracked_output, word_subtitles, subtitled_output)
            transcription_text, transcription_segments = transcription_of_audio(subtitled_output)
            keywords = extract_keywords(transcription_text)
            image_paths = download_images(keywords)
            keyword_timestamps = get_keyword_timestamps(transcription_segments, keywords)
            add_images_to_video(subtitled_output, keyword_timestamps, image_paths, final_output)

            final_path = os.path.join(app.config['PROCESSED_FOLDER'], final_output)
            os.rename(final_output, final_path)
            return redirect(url_for('download_file', filename=final_output))

    return render_template('process.html', filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)