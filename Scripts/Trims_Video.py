import ffmpeg
import os

def trim_video_original_start_to_end(input_video_path, output_video_path, start_time, end_time):
    try:
        if not os.path.exists(input_video_path):
            print(f"Error: Video file not found at {input_video_path}")
            return

        output_dir = os.path.dirname(output_video_path)
        os.makedirs(output_dir, exist_ok=True)

        print(f"🔹 Trimming video: {input_video_path}")
        print(f"🔹 Output will be saved at: {output_video_path}")
        (
            ffmpeg
            .input(input_video_path, ss=start_time, to=end_time)
            .output(output_video_path, c="copy")
            .run(overwrite_output=True)
        )

        print(f"Video trimmed successfully and saved to {output_video_path}")

    except ffmpeg.Error as e:
        print(f"FFmpeg error while trimming video: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

