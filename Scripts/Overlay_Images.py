from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os

def get_keyword_timestamps(transcription_segments, keywords):
    keyword_timestamps = {}

    for segment in transcription_segments:
        text = segment["text"]
        start = segment["start"]
        end = segment["end"]

        for keyword in keywords:
            if keyword.lower() in text.lower():
                if keyword not in keyword_timestamps:
                    keyword_timestamps[keyword] = []
                keyword_timestamps[keyword].append((max(0, start - 0.5), end + 0.5))  

    return keyword_timestamps

def get_first_image_path(folder):
    if os.path.exists(folder):
        files = [f for f in os.listdir(folder) if f.endswith((".jpg", ".png", ".jpeg"))]
        return os.path.join(folder, files[0]) if files else None
    return None

def add_images_to_video(video_path, keyword_timestamps, image_paths, output_path):
    video = VideoFileClip(video_path)
    video_w, video_h = video.size  

    overlays = []

    for keyword, timestamps in keyword_timestamps.items():
        img_path = get_first_image_path(image_paths[keyword])

        if not img_path:
            print(f"No valid image found for {keyword}")
            continue

        img_clip = (ImageClip(img_path, transparent=True)
                    .set_duration(1.0)
                    .resize(width=video_w * 0.8)
                    .set_opacity(1))

        for start, end in timestamps:
            fade_duration = 0.2
            print(f"Overlaying {keyword} from {start}s to {end}s")

            clip = (img_clip
                    .set_position(("center", "top"))
                    .set_start(start)
                    .set_duration(end - start)
                    .crossfadein(fade_duration)
                    .crossfadeout(fade_duration))

            overlays.append(clip)

    if not overlays:
        print("No overlays were added. Check timestamps and image paths.")

    final_video = CompositeVideoClip([video] + overlays, size=(video_w, video_h))
    final_video.write_videofile(output_path, fps=video.fps, codec="libx264", threads=4)
