import cv2
import numpy as np
import webrtcvad
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from collections import deque

def extract_audio(video_path, audio_output="temp.wav"):
    """Extracts audio from video."""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output, codec="pcm_s16le")
    return audio_output, video.audio

def detect_speech(audio_path, aggressiveness=3):
    """Detects speech segments using WebRTC VAD."""
    audio = AudioSegment.from_file(audio_path, format="wav").set_frame_rate(16000).set_channels(1)
    vad = webrtcvad.Vad(aggressiveness)

    speech_intervals = []
    samples_per_window = int(audio.frame_rate * 0.03)  # 30ms chunks

    for i in range(0, len(audio.raw_data), samples_per_window * 2):
        chunk = audio.raw_data[i:i + samples_per_window * 2]
        if len(chunk) < samples_per_window * 2:
            continue
        if vad.is_speech(chunk, audio.frame_rate):
            timestamp = i / (audio.frame_rate * 2)
            speech_intervals.append((timestamp, timestamp + 0.03))

    return speech_intervals

def load_face_detector():
    """Loads a pre-trained face detector."""
    return cv2.dnn.readNetFromCaffe("deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel")

def detect_faces(frame, net):
    """Detects faces in a given frame."""
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype("int")
            faces.append((x1, y1, x2 - x1, y2 - y1))

    return faces

def process_video(input_path, output_path, speech_intervals, detection_skip=5, smoothing_window=5):
    """Processes video to track speakers and apply smooth cropping."""
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    output_width, output_height = 720, 1280  # 9:16 aspect ratio
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("temp_video.mp4", fourcc, fps, (output_width, output_height))

    net = load_face_detector()
    frame_number, last_detected_faces = 0, []
    bbox_history = deque(maxlen=smoothing_window)
    last_speaker_bbox = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = frame_number / fps
        in_speech = any(start <= current_time <= end for (start, end) in speech_intervals)

        if in_speech:
            if frame_number % detection_skip == 0 or not last_detected_faces:
                last_detected_faces = detect_faces(frame, net)

            if last_detected_faces:
                x, y, w, h = last_detected_faces[0]
                bbox_history.append((x, y, w, h))
                smoothed_bbox = np.mean(bbox_history, axis=0).astype(int)
                last_speaker_bbox = smoothed_bbox
            else:
                smoothed_bbox = last_speaker_bbox

        else:
            smoothed_bbox = last_speaker_bbox

        if smoothed_bbox is not None:
            x, y, w, h = smoothed_bbox
            person_roi = frame[y:y + h, x:x + w]
            resized = cv2.resize(person_roi, (output_width, output_height))
        else:
            resized = cv2.resize(frame, (output_width, output_height))

        out.write(resized)
        frame_number += 1

    cap.release()
    out.release()
