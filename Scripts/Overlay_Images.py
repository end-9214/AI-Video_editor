from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os

def add_images_to_video(video_path, keyword_timestamps, image_paths, output_path):
    """Overlays images on the video based on detected timestamps."""
    video = VideoFileClip(video_path)
    video_w, video_h = video.size

    overlays = []
    for keyword, timestamps in keyword_timestamps.items():
        img_path = os.path.join(image_paths[keyword], os.listdir(image_paths[keyword])[0])
        if not os.path.exists(img_path):
            continue

        img_clip = ImageClip(img_path).set_duration(1.0).resize(width=video_w * 0.8).set_opacity(1)

        for start, end in timestamps:
            overlays.append(img_clip.set_position(("center", "top")).set_start(start).set_duration(end - start))

    final_video = CompositeVideoClip([video] + overlays, size=(video_w, video_h))
    final_video.write_videofile(output_path, fps=video.fps, codec="libx264")
