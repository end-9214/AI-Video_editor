import cv2
import numpy as np
import webrtcvad
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from collections import deque

def extract_audio(video_path, audio_output="temp.wav"):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output, codec="pcm_s16le")
    return audio_output, video.audio  

def detect_speech(audio_path, aggressiveness=3):
    audio = AudioSegment.from_file(audio_path, format="wav")
    audio = audio.set_frame_rate(16000).set_channels(1)
    vad = webrtcvad.Vad(aggressiveness)

    speech_intervals = []
    window_duration = 0.03  
    frame_rate = audio.frame_rate
    samples_per_window = int(frame_rate * window_duration)

    for i in range(0, len(audio.raw_data), samples_per_window * 2):  
        chunk = audio.raw_data[i:i + samples_per_window * 2]
        if len(chunk) < samples_per_window * 2:
            continue
        is_speech = vad.is_speech(chunk, frame_rate)
        timestamp = i / (frame_rate * 2)
        if is_speech:
            speech_intervals.append((timestamp, timestamp + window_duration))

    return speech_intervals

def load_face_detector():
    net = cv2.dnn.readNetFromCaffe(
        "Scripts/deploy.prototxt",
        "Scripts/res10_300x300_ssd_iter_140000.caffemodel"
    )
    return net

def detect_faces(frame, net):
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
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(x2, w), min(y2, h)  
            faces.append((x1, y1, x2 - x1, y2 - y1))
    return faces

def moving_average(values, window_size=5):
    if not values:
        return None
    smoothed = np.mean(values, axis=0).astype(int)
    return tuple(smoothed)

def process_video(input_path, output_path, speech_intervals, detection_skip=5, smoothing_window=10):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_width = 720
    output_height = 1280
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("temp_video.mp4", fourcc, fps, (output_width, output_height))

    net = load_face_detector()
    frame_number = 0
    last_detected_faces = []
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

            if len(last_detected_faces) == 0:
                smoothed_bbox = last_speaker_bbox
            else:
                if len(last_detected_faces) == 1:
                    x, y, w, h = last_detected_faces[0]

                    expand_factor = 3.2  
                    x_new = max(0, int(x - (w * (expand_factor - 1) / 2)))
                    w_new = min(width - x_new, int(w * expand_factor))
                    y_new = max(0, int(y - (h * (expand_factor - 1) / 2)))
                    h_new = min(height - y_new, int(h * expand_factor))

                    bbox_history.append((x_new, y_new, w_new, h_new))
                    smoothed_bbox = moving_average(list(bbox_history))

                    last_speaker_bbox = smoothed_bbox  
                else:
                    stacked_frames = []
                    for x, y, w, h in last_detected_faces[:2]:
                        expand_factor = 3.2
                        x_new = max(0, int(x - (w * (expand_factor - 1) / 2)))
                        w_new = min(width - x_new, int(w * expand_factor))
                        y_new = max(0, int(y - (h * (expand_factor - 1) / 2)))
                        h_new = min(height - y_new, int(h * expand_factor))

                        bbox_history.append((x_new, y_new, w_new, h_new))
                        smoothed_bbox = moving_average(list(bbox_history))

                        x_s, y_s, w_s, h_s = smoothed_bbox
                        person_roi = frame[y_s:y_s + h_s, x_s:x_s + w_s]
                        resized_person = cv2.resize(person_roi, (output_width, output_height // 2))
                        stacked_frames.append(resized_person)

                    if len(stacked_frames) == 2:
                        padded_frame = np.vstack(stacked_frames)
                    else:
                        padded_frame = stacked_frames[0]

                    out.write(padded_frame)
                    frame_number += 1
                    continue  
        else:
            smoothed_bbox = last_speaker_bbox

        if smoothed_bbox:
            x_s, y_s, w_s, h_s = smoothed_bbox
            person_roi = frame[y_s:y_s + h_s, x_s:x_s + w_s]

            aspect_ratio = w_s / h_s
            target_aspect_ratio = output_width / output_height

            if aspect_ratio > target_aspect_ratio:
                new_width = output_width
                new_height = int(output_width / aspect_ratio)
            else:
                new_height = output_height
                new_width = int(output_height * aspect_ratio)

            resized = cv2.resize(person_roi, (new_width, new_height))


            padded_frame = np.zeros((output_height, output_width, 3), dtype=np.uint8)
            start_x = (output_width - new_width) // 2
            start_y = (output_height - new_height) // 2
            padded_frame[start_y:start_y + new_height, start_x:start_x + new_width] = resized
        else:
            resized = cv2.resize(frame, (output_width, int(output_width * height / width)))
            padded_frame = np.zeros((output_height, output_width, 3), dtype=np.uint8)
            start_y = (output_height - resized.shape[0]) // 2
            padded_frame[start_y:start_y + resized.shape[0], :, :] = resized

        out.write(padded_frame)
        frame_number += 1

    cap.release()
    out.release()

