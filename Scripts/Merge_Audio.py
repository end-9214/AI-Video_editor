from moviepy.editor import VideoFileClip

def merge_audio(video_path, audio_clip, output_path):
    """Merges processed video with original audio."""
    video = VideoFileClip(video_path)
    video = video.set_audio(audio_clip)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")
