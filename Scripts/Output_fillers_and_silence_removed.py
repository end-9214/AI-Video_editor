import subprocess
from pydub import AudioSegment

def get_keep_ranges(all_trim_ranges, audio_file_path):
    try:
        audio = AudioSegment.from_file(audio_file_path)
        keep_ranges = []
        current_start = 0

        all_trim_ranges.sort()

        for start, end in all_trim_ranges:
            keep_ranges.append((current_start, start))
            current_start = end

        if current_start < len(audio) / 1000.0:
            keep_ranges.append((current_start, len(audio) / 1000.0))

        keep_ranges = [r for r in keep_ranges if r[0] < r[1]]
        print(f"Keep Ranges: {keep_ranges}")

        return keep_ranges
    except Exception as e:
        print(f"Error computing keep ranges: {e}")
        return []

def trim_video(input_video, output_video, keep_ranges):
    if not keep_ranges:
        print("No valid keep ranges found. Skipping video trimming.")
        return

    filter_str = f"select='{'+'.join([f'between(t,{s},{e})' for s, e in keep_ranges])}',setpts=N/FRAME_RATE/TB"

    cmd = [
        "ffmpeg",
        "-i", input_video,
        "-vf", filter_str,
        "-af", f"aselect='{'+'.join([f'between(t,{s},{e})' for s, e in keep_ranges])}',asetpts=N/SR/TB",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        output_video
    ]

    subprocess.run(cmd)
    print(f"Video trimmed successfully and saved to {output_video}")
