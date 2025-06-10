import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os
import re
import subprocess
import shutil
import vlc

# --- Core App Class ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Visual YouTube Trimmer (v10 - Guided Workflow)")
        self.geometry("800x800")
        ctk.set_appearance_mode("Dark")
        self.yt_info = None; self.video_duration = 0; self.is_seeking = False
        self.output_folder = os.path.join(os.path.expanduser("~"), "Videos")
        try:
            self.vlc_instance = vlc.Instance(); self.player = self.vlc_instance.media_player_new()
        except Exception as e:
            messagebox.showerror("VLC Error", f"Could not initialize VLC. Is it installed?\nError: {e}"); self.destroy(); return
        self.create_widgets()
        self.check_ffmpeg()
        self.after(100, self.update_player_time)

    def create_widgets(self):
        # (This function is identical to the previous version)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        url_frame = ctk.CTkFrame(self); url_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew"); url_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(url_frame, text="YouTube URL:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="Right-click to paste..."); self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.add_right_click_menu(self.url_entry)
        self.fetch_button = ctk.CTkButton(url_frame, text="Fetch & Preview", command=self.start_fetch_thread); self.fetch_button.grid(row=0, column=2, padx=10, pady=10)
        self.video_frame = ctk.CTkFrame(self, fg_color="black"); self.video_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.control_frame = ctk.CTkFrame(self); self.control_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew"); self.control_frame.grid_columnconfigure(1, weight=1)
        self.title_label = ctk.CTkLabel(self.control_frame, text="Title: (Fetch a video first)", wraplength=750, justify="left"); self.title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="w")
        self.play_pause_button = ctk.CTkButton(self.control_frame, text="▶ Play", width=80, command=self.toggle_play_pause); self.play_pause_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.current_time_label = ctk.CTkLabel(self.control_frame, text="00:00:00 / 00:00:00"); self.current_time_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.start_time_label = ctk.CTkLabel(self.control_frame, text="Start: 00:00:00"); self.start_time_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        self.start_slider = ctk.CTkSlider(self.control_frame, from_=0, to=100, command=self.start_slider_update); self.start_slider.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        self.end_time_label = ctk.CTkLabel(self.control_frame, text="End: 00:00:00"); self.end_time_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        self.end_slider = ctk.CTkSlider(self.control_frame, from_=0, to=100, command=self.end_slider_update); self.end_slider.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        output_frame = ctk.CTkFrame(self); output_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew"); output_frame.grid_columnconfigure(2, weight=1)
        ctk.CTkLabel(output_frame, text="Output Format:").grid(row=0, column=0, padx=10, pady=10)
        self.format_selector = ctk.CTkSegmentedButton(output_frame, values=["Video", "Audio"], command=self.format_changed); self.format_selector.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.filename_entry = ctk.CTkEntry(output_frame); self.filename_entry.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.settings_button = ctk.CTkButton(output_frame, text="⚙️ Settings", width=100, command=self.open_settings); self.settings_button.grid(row=0, column=3, padx=10, pady=10)
        action_frame = ctk.CTkFrame(self); action_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew"); action_frame.grid_columnconfigure(0, weight=1)
        self.trim_button = ctk.CTkButton(action_frame, text="Trim & Save", command=self.start_trim_thread); self.trim_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.status_label = ctk.CTkLabel(action_frame, text="Status: Idle", text_color="gray"); self.status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Start with all interactive controls disabled, except the fetch button.
        self.set_all_interactive_controls("disabled")
        self.fetch_button.configure(state="normal")
        self.url_entry.configure(state="normal")

    def set_all_interactive_controls(self, state="disabled"):
        """Disables or enables ALL controls that the user can interact with post-fetch."""
        self.play_pause_button.configure(state=state)
        self.start_slider.configure(state=state)
        self.end_slider.configure(state=state)
        self.format_selector.configure(state=state)
        self.filename_entry.configure(state=state)
        self.settings_button.configure(state=state)
        self.trim_button.configure(state=state)

    def set_trim_controls(self, state="disabled"):
        """Manages only the controls related to the actual trimming action."""
        self.start_slider.configure(state=state)
        self.end_slider.configure(state=state)
        self.filename_entry.configure(state=state)
        self.settings_button.configure(state=state)
        if state == "normal" and shutil.which("ffmpeg"):
            self.trim_button.configure(state="normal")
        else:
            self.trim_button.configure(state="disabled")

    def format_changed(self, value):
        """Called when the Video/Audio button is clicked."""
        if not self.yt_info: return

        # --- NEW LOGIC: This is now the trigger to unlock trimming ---
        self.set_trim_controls("normal")

        # Auto-populate the filename
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", self.yt_info['title'])
        new_ext = ".mp4" if value == "Video" else ".mp3"
        self.filename_entry.delete(0, "end")
        self.filename_entry.insert(0, f"{sanitized_title}{new_ext}")
        self.update_status("Ready to trim.", "lightgreen")

    def load_video_into_player(self, stream_url):
        media = self.vlc_instance.media_new(stream_url)
        self.player.set_media(media)
        self.player.set_hwnd(self.video_frame.winfo_id())
        self.title_label.configure(text=f"Title: {self.yt_info['title']}")
        self.start_slider.configure(to=self.video_duration, number_of_steps=int(self.video_duration))
        self.end_slider.configure(to=self.video_duration, number_of_steps=int(self.video_duration))
        self.start_slider.set(0)
        self.end_slider.set(self.video_duration)
        self._update_time_labels()

        # --- NEW LOGIC: Enable only the player and format selector ---
        self.fetch_button.configure(state="normal")
        self.play_pause_button.configure(state="normal")
        self.format_selector.configure(state="normal")

        self.update_status("Preview loaded. Select Video or Audio to enable trimming.", "lightgreen")
        self.player.play()

    def start_fetch_thread(self):
        self.set_all_interactive_controls("disabled")
        self.fetch_button.configure(state="disabled")
        self.status_label.configure(text="Status: Fetching video info...", text_color="yellow")
        thread = threading.Thread(target=self.fetch_and_load_video)
        thread.start()

    def download_and_trim_final(self):
        temp_dir = os.path.join(self.output_folder, "yt_trimmer_temp")
        os.makedirs(temp_dir, exist_ok=True)
        try:
            url, is_audio_only = self.yt_info['webpage_url'], (self.format_selector.get() == "Audio")
            self.after(0, self.update_status, f"Status: Downloading final high-quality {'audio' if is_audio_only else 'video'}...", "yellow")
            ydl_opts = {'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'), 'quiet': True,'format': 'bestaudio/best' if is_audio_only else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
            temp_download_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])
            self.after(0, self.update_status, "Status: Trimming with FFmpeg...", "yellow")
            start_time, end_time = self.start_slider.get(), self.end_slider.get()
            final_output_path = os.path.join(self.output_folder, self.filename_entry.get())
            command = ['ffmpeg', '-i', temp_download_path, '-ss', self.format_time(start_time), '-to', self.format_time(end_time)]
            if is_audio_only: command.extend(['-vn', '-c:a', 'libmp3lame', '-ab', '192k'])
            else: command.extend(['-c', 'copy'])
            command.extend(['-y', final_output_path])
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            if result.returncode != 0: raise Exception(f"FFmpeg failed: {result.stderr}")
            self.after(0, self.update_status, f"Success! Saved to {final_output_path}", "lightgreen")
        except Exception as e:
            self.after(0, self.update_status, f"Error: {e}", "red")
        finally:
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
            # Re-enable all controls so the user can perform another action
            self.after(0, lambda: self.set_all_interactive_controls("normal"))
            self.after(0, lambda: self.fetch_button.configure(state="normal"))

    # The rest of the functions are unchanged and correct.
    def add_right_click_menu(self, widget):
        menu = tk.Menu(widget, tearoff=0, bg="#2B2B2B", fg="white", bd=0)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: (widget.focus_set(), widget.event_generate('<<Paste>>')))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: widget.event_generate("<<SelectAll>>"))
        widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))
    def open_settings(self): SettingsWindow(self)
    def _update_time_labels(self):
        self.start_time_label.configure(text=f"Start: {self.format_time(self.start_slider.get())}")
        self.end_time_label.configure(text=f"End: {self.format_time(self.end_slider.get())}")
    def start_slider_update(self, value):
        if value > self.end_slider.get(): self.end_slider.set(value)
        self._update_time_labels()
        if not self.is_seeking:
            self.is_seeking = True; self.player.set_time(int(value * 1000)); self.after(200, self.release_seek_lock)
    def end_slider_update(self, value):
        if value < self.start_slider.get(): self.start_slider.set(value)
        self._update_time_labels()
    def release_seek_lock(self):
        self.is_seeking = False
        if not self.player.is_playing(): self.player.play(); self.player.pause()
    def update_player_time(self):
        if self.yt_info and self.player.get_state() != vlc.State.Ended:
            current_sec = self.player.get_time() / 1000.0
            self.current_time_label.configure(text=f"{self.format_time(current_sec)} / {self.format_time(self.video_duration)}")
            end_sec = self.end_slider.get()
            if current_sec >= end_sec and self.player.is_playing():
                self.player.set_time(int(self.start_slider.get() * 1000))
        self.after(250, self.update_player_time)
    def fetch_and_load_video(self):
        try:
            url = self.url_entry.get()
            if not url: raise ValueError("URL cannot be empty.")
            with yt_dlp.YoutubeDL({'quiet': True, 'source_address': '0.0.0.0'}) as ydl: self.yt_info = ydl.extract_info(url, download=False)
            self.video_duration = self.yt_info.get('duration', 0)
            if not self.video_duration: raise ValueError("Could not get video duration.")
            stream_url=None; formats=self.yt_info.get('formats', [self.yt_info]); preferred_formats=['22', '18']
            for fmt_id in preferred_formats:
                for f in formats:
                    if f.get('format_id') == fmt_id: stream_url = f.get('url'); break
                if stream_url: break
            if not stream_url: stream_url = next((f['url'] for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none'), None)
            if not stream_url: stream_url = self.yt_info.get('url')
            if not stream_url: raise ValueError("Could not find a streamable URL. Try updating yt-dlp: python -m pip install --upgrade yt-dlp")
            self.after(0, self.load_video_into_player, stream_url)
        except Exception as e:
            self.after(0, self.update_status, f"Status: Error - {e}", "red")
            self.after(0, lambda: self.fetch_button.configure(state="normal"))
    def toggle_play_pause(self):
        if self.player.is_playing(): self.player.pause(); self.play_pause_button.configure(text="▶ Play")
        else: self.player.play(); self.play_pause_button.configure(text="❚❚ Pause")
    def start_trim_thread(self):
        self.player.stop(); self.set_all_interactive_controls("disabled"); self.fetch_button.configure(state="disabled")
        thread = threading.Thread(target=self.download_and_trim_final); thread.start()
    def check_ffmpeg(self):
        if not shutil.which("ffmpeg"): self.update_status("Error: ffmpeg not found in system PATH.", "red")
    def format_time(self, seconds):
        h=int(seconds//3600); m=int((seconds%3600)//60); s=int(seconds%60); return f"{h:02d}:{m:02d}:{s:02d}"
    def update_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
    def on_closing(self):
        self.player.stop(); self.destroy()

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master); self.master_app = master; self.title("Settings"); self.geometry("500x150")
        self.transient(master); self.grab_set(); self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Output Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.folder_entry = ctk.CTkEntry(self, placeholder_text=self.master_app.output_folder)
        self.folder_entry.grid(row=0, column=1, padx=(0,10), pady=10, sticky="ew"); self.folder_entry.insert(0, self.master_app.output_folder)
        browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_folder); browse_button.grid(row=0, column=2, padx=10, pady=10)
        save_button = ctk.CTkButton(self, text="Save & Close", command=self.save_and_close); save_button.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
    def browse_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.master_app.output_folder)
        if folder_path: self.folder_entry.delete(0, "end"); self.folder_entry.insert(0, folder_path)
    def save_and_close(self):
        new_path = self.folder_entry.get()
        if os.path.isdir(new_path):
            self.master_app.output_folder = new_path; self.master_app.update_status(f"Output folder set to: {new_path}", "gray"); self.destroy()
        else: messagebox.showerror("Invalid Path", "The selected path is not a valid directory.")

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
