# ✂️YoutubeTrimmer v1



Ever wanted to clip a specific part of a YouTube video without downloading the whole thing and using complex editors like Premiere Pro or After Effects? **YouTubeTrimmer** is the tool you've been waiting for!

This sleek, modern desktop app lets you visually trim any YouTube video or audio with an intuitive, interactive player. Just drag the sliders to your desired start and end points, choose your quality, and get a perfectly trimmed clip in seconds.


## SCREENSHOTS
![image](https://github.com/user-attachments/assets/7de8037a-4071-4196-a698-766990fdc5e0)



---

## 🔥 Key Features

-   **Interactive Video Preview:** No more guessing timestamps! Paste a URL and get an instant video preview.
-   **Visual Trimming:** Drag the 'Start' and 'End' sliders to intuitively select your desired clip. The player seeks to your start point instantly for precise editing.
-   **Audio & Video Trimming:** Easily switch between saving your clip as a video (`.mp4`) or just the audio (`.mp3` or `.m4a`).
-   **Advanced Quality Control:** Don't settle for default quality. Open the settings to see *all* available video and audio formats for that specific video and choose the exact one you need.
-   **Blazingly Fast:** Powered by the industry-standard `yt-dlp` and `ffmpeg`, using stream-copy for video trims which is incredibly fast (no re-encoding!).
-   **Modern UI:** Built with CustomTkinter for a clean, professional look that feels great to use.
-   **Smart Workflow:** The app guides you through the process, unlocking controls as you make selections to prevent errors.

---

## ⚙️ How It Works Under the Hood

This isn't just a simple script; it's a powerful combination of best-in-class tools:

1.  **`yt-dlp`**: The most robust and actively maintained tool for fetching video metadata and stream URLs from YouTube. It's the reliable backbone of our application.
2.  **`python-vlc`**: This library acts as a "remote control" for the powerful VLC Media Player, allowing us to embed a live video preview directly into our application window.
3.  **`ffmpeg`**: The undisputed champion of video manipulation. We call it directly to perform lightning-fast, lossless trims on video files.
4.  **`CustomTkinter`**: Provides the beautiful, modern graphical user interface (GUI).

---

## 🚀 Installation & Setup

Getting started is easy, but you need to install a few things first.
## 1st Method
### Step 1: Install Dependencies

This project relies on a few key applications and Python libraries.

#### Application Dependencies:
You must have **VLC Media Player** and **FFmpeg** installed on your system.

-   **VLC Media Player:**
    -   Download and install it from the [**official VideoLAN website**](https://www.videolan.org/vlc/).
-   **FFmpeg:**
    -   **Windows:** Download the executable from the [**official FFmpeg website**](https://ffmpeg.org/download.html). Unzip the file, find the `bin` folder, and **add that folder's path to your system's PATH environment variable.** (This is a crucial step!)
    -   **macOS (Recommended):** Use Homebrew: `brew install ffmpeg`
    -   **Linux (Debian/Ubuntu):** Use your package manager: `sudo apt install ffmpeg`

#### Python Libraries:
Open your terminal or command prompt and run the following command to install the necessary Python packages:

```bash
pip install customtkinter yt-dlp python-vlc
```

### Step 2: Clone the Repository

<!-- You can link to your GitHub repo here if you have one -->
<!-- Or you can use a collapsible block for the code -->

```
git clone https://github.com/Abhaikumar007/YoutubeTrimmer/
cd YoutubeTrimmer
python3 yt-trimmer.py
```

---
## 2nd Method (Supports Windows Only)
- Go to `Releases` Section and download the exe version



## 📖 How to Use the Trimmer

The guided workflow makes trimming a breeze.

1.  **Paste the URL:** Paste any YouTube video URL into the top entry box. You can use `Ctrl+V` or right-click to paste.

    <!-- ADD A SCREENSHOT OF THE INITIAL APP WINDOW HERE -->

2.  **Fetch & Preview:** Click the "Fetch & Preview" button. The app will load the video's info and an interactive player. Notice the "Output Format" label is glowing, guiding you to the next step!

    <!-- ADD A SCREENSHOT SHOWING THE LOADED PREVIEW AND GLOWING LABEL -->

3.  **Choose Your Format:** This is the key step! Select whether you want to save a **"Video"** or **"Audio"** file. Once you click, the trimming controls will unlock.

    <!-- ADD A SCREENSHOT OF THE UNLOCKED CONTROLS -->

4.  **Trim Visually:**
    -   Drag the **Start** slider to set your clip's beginning. The video will instantly jump to that point.
    -   Drag the **End** slider to set the end point. Playback will continue smoothly, only looping if it passes your new end time.

5.  **Fine-Tune with Settings (Optional):**
    -   Click the **"⚙️ Settings"** button to open the advanced options.
    -   Here, you can change the output folder and select a specific video or audio quality from dropdowns that are *dynamically generated for that video*.



6.  **Trim & Save!**
    -   Check that the auto-generated filename is what you want.
    -   Click the big **"Trim & Save"** button. The app will download the final, high-quality version of your selection, trim it, and save it to your chosen folder.

Enjoy your perfectly clipped content!



This project was built with a focus on user experience and robust functionality. We hope you find it as useful as we do
