import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import cv2
import os
import threading

from Scripts.Convert_to_Audio import convert_video_to_audio
from Scripts.Transcription_script import transcription_of_audio, extract_filler_words
from Scripts.Silence_and_fillers_removal import detect_silence_ranges, identify_filler_ranges, combine_silence_and_fillers
from Scripts.Cleaned_audio_script import remove_silence_and_fillers
from Scripts.Output_fillers_and_silence_removed import get_keep_ranges, trim_video
from Scripts.Trims_Video import trim_video_original_start_to_end

# Color Scheme
BG_COLOR = "#2d2d2d"
PRIMARY_COLOR = "#6c5ce7"
SECONDARY_COLOR = "#a8a5e6"
ACCENT_COLOR = "#ff7675"
TEXT_COLOR = "#ffffff"

class VideoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Video Editor")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_COLOR)
        self.video_path = None
        self.processing = False
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.api_key_screen()

    def configure_styles(self):
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TButton', 
                           font=('Segoe UI', 12),
                           borderwidth=0,
                           relief='flat',
                           background=PRIMARY_COLOR,
                           foreground=TEXT_COLOR)
        self.style.map('TButton',
                      background=[('active', SECONDARY_COLOR), ('disabled', BG_COLOR)],
                      foreground=[('active', TEXT_COLOR), ('disabled', TEXT_COLOR)])
        
        self.style.configure('TEntry', 
                           font=('Segoe UI', 12),
                           fieldbackground=BG_COLOR,
                           foreground=TEXT_COLOR,
                           insertcolor=TEXT_COLOR)
        
        self.style.configure('TLabel',
                           background=BG_COLOR,
                           foreground=TEXT_COLOR,
                           font=('Segoe UI', 12))
        
        self.style.configure('Vertical.TProgressbar',
                           thickness=20,
                           troughcolor=BG_COLOR,
                           background=ACCENT_COLOR,
                           lightcolor=ACCENT_COLOR,
                           darkcolor=ACCENT_COLOR)

    def api_key_screen(self):
        self.clear_screen()
        
        container = ttk.Frame(self.root)
        container.pack(expand=True, fill='both', padx=50, pady=50)
        
        ttk.Label(container, text="🔑 Welcome to AI Video Editor", 
                font=('Segoe UI', 20, 'bold')).pack(pady=20)
        
        ttk.Label(container, text="Enter your Groq API Key to continue:", 
                font=('Segoe UI', 14)).pack(pady=10)
        
        self.api_key_entry = ttk.Entry(container, font=('Segoe UI', 14), width=30)
        self.api_key_entry.pack(pady=20, ipady=8)
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Submit", style='TButton', 
                 command=self.submit_api_key).pack(side=tk.LEFT, padx=10)

    def main_screen(self):
        self.clear_screen()
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header = ttk.Frame(main_container)
        header.pack(fill='x', pady=10)
        ttk.Button(header, text="Select Video", command=self.select_video,
                 style='TButton').pack(side=tk.LEFT)
        ttk.Label(header, text="AI Video Editor", font=('Segoe UI', 18, 'bold'),
                foreground=PRIMARY_COLOR).pack(side=tk.RIGHT)
        
        # Video Preview
        preview_frame = ttk.LabelFrame(main_container, text="Video Preview",
                                     style='TLabel')
        preview_frame.pack(fill='both', expand=True, pady=20)
        self.video_label = ttk.Label(preview_frame, background=BG_COLOR)
        self.video_label.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Control Panel
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill='x', pady=20)
        
        self.progress = ttk.Progressbar(control_frame, 
                                      style='Vertical.TProgressbar',
                                      length=400)
        self.progress.pack(side=tk.LEFT, padx=20)
        
        btn_container = ttk.Frame(control_frame)
        btn_container.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(btn_container, text="Run Main Pipeline", 
                 command=self.run_main_pipeline).pack(fill='x', pady=10)
        ttk.Button(btn_container, text="Run Final Pipeline",
                 command=self.run_final_pipeline).pack(fill='x', pady=10)
        
        # Status Bar
        self.status = ttk.Label(main_container, text="Ready",
                              font=('Segoe UI', 10))
        self.status.pack(side=tk.BOTTOM, fill='x')

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if self.video_path:
            self.preview_video(self.video_path)
            self.status.config(text=f"Loaded: {os.path.basename(self.video_path)}")

    def preview_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).resize((640, 360), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=imgtk)
            self.video_label.image = imgtk
        cap.release()

    def run_main_pipeline(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video first")
            return
            
        
        self.toggle_processing(True)
        threading.Thread(target=self.process_main_pipeline, daemon=True).start()

    def process_main_pipeline(self):
        try:
            output_video = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4")],
                title="Save processed video"
            )
            if not output_video:
                self.toggle_processing(False)
                return

            trim_choice = messagebox.askyesno("Trimming", "Do you want to trim the video?")
            input_video = self.video_path
            temp_files = []

            if trim_choice:
                start_time = simpledialog.askstring("Start Time", "Enter start time (seconds or HH:MM:SS):")
                end_time = simpledialog.askstring("End Time", "Enter end time (seconds or HH:MM:SS):")
                
                if not start_time or not end_time:
                    messagebox.showwarning("Warning", "Trimming canceled")
                    self.toggle_processing(False)
                    return
                
                trimmed_output = "trimmed_temp.mp4"
                temp_files.append(trimmed_output)
                self.update_status("Trimming video...")
                trim_video_original_start_to_end(input_video, trimmed_output, start_time, end_time)
                input_video = trimmed_output

            self.update_status("Converting video to audio...")
            audio_file = convert_video_to_audio(input_video)
            if not audio_file:
                raise Exception("Audio conversion failed")
            temp_files.append(audio_file)

            self.update_status("Transcribing audio...")
            transcribed_text, segments = transcription_of_audio(audio_file)
            if not transcribed_text or not segments:
                raise Exception("Transcription failed")

            self.update_status("Analyzing filler words...")
            filler_words = extract_filler_words(transcribed_text)
            
            self.update_status("Detecting silences...")
            silence_ranges = detect_silence_ranges(audio_file)
            
            self.update_status("Identifying filler ranges...")
            filler_ranges = identify_filler_ranges(segments, filler_words)
            
            self.update_status("Processing audio...")
            all_trim_ranges = combine_silence_and_fillers(silence_ranges, filler_ranges)
            keep_ranges = get_keep_ranges(all_trim_ranges, audio_file)
            
            self.update_status("Cleaning audio...")
            cleaned_audio = remove_silence_and_fillers(audio_file, all_trim_ranges)
            temp_files.append(cleaned_audio)
            
            self.update_status("Generating final video...")
            trim_video(input_video, output_video, keep_ranges)
            
            # Cleanup temporary files
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
            
            self.update_status("Processing complete!")
            messagebox.showinfo("Success", f"Video saved to:\n{output_video}")
            self.toggle_processing(False)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Processing Error", str(e))
            self.toggle_processing(False)
            # Cleanup temp files on error
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)

    def run_final_pipeline(self):
        # Implement your Final_pipeline.py logic here
        messagebox.showinfo("Info", "Final pipeline not implemented yet")

    def update_status(self, message):
        self.status.config(text=message)
        self.root.update_idletasks()

    def toggle_processing(self, processing):
        state = 'disabled' if processing else 'normal'
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                child['state'] = state
        if processing:
            self.progress.start(10)
        else:
            self.progress.stop()

    def submit_api_key(self):
        api_key = self.api_key_entry.get()
        if api_key:
            self.main_screen()
        else:
            messagebox.showerror("Error", "Please enter a valid API key")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorApp(root)
    root.mainloop()