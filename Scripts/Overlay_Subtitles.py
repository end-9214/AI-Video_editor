import moviepy.editor as mp
import cv2
import numpy as np

def overlay_live_subtitles(video_path, subtitles, output_path):
    try:
        video = mp.VideoFileClip(video_path)

        def add_text(get_frame, t):
            frame = get_frame(t)
            h, w, _ = frame.shape

            overlay = frame.copy()
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.2
            font_thickness = 3
            text_color = (255, 255, 255)
            bg_color = (0, 0, 0)

            current_text = " ".join(
                [word_info["word"] for word_info in subtitles if word_info["start"] <= t <= word_info["end"]]
            )

            if current_text:
                text_size = cv2.getTextSize(current_text, font, font_scale, font_thickness)[0]
                text_x = (w - text_size[0]) // 2
                text_y = h - 100

                padding = 20
                bg_x1, bg_y1 = text_x - padding, text_y - text_size[1] - padding
                bg_x2, bg_y2 = text_x + text_size[0] + padding, text_y + padding
                cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)

                alpha = 0.5
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                cv2.putText(frame, current_text, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

            return frame

        new_video = video.fl(add_text)
        new_video.write_videofile(output_path, fps=video.fps, codec="libx264", threads=4)

        print(f"Subtitled video saved as {output_path}")

    except Exception as e:
        print(f"Error overlaying subtitles: {e}")