import subprocess
import os

def convert_video_to_audio(input_video_path):
    try:
        input_video_name = os.path.splitext(os.path.basename(input_video_path))[0]
        output_audio_path = f"{input_video_name}.mp3"

        command = [
            "ffmpeg",
            "-i", input_video_path,
            "-vn",
            "-q:a", "0",
            "-map", "a",
            output_audio_path
        ]

        subprocess.run(command, check=True)
        print(f"Audio extracted successfully: {output_audio_path}")
        return output_audio_path

    except subprocess.CalledProcessError:
        print("Error extracting audio with FFmpeg.")
        return None
