# 📸 foto-kita-blur

A playful, real‑time Computer Vision demo that detects a **peace sign** (✌️) from your webcam, applies a **Gaussian blur**, plays a fun sound effect, and surrounds the frame with a border of tiny pink‑love emojis.

![demo](https://via.placeholder.com/800x450/000000/FFFFFF?text=Demo+GIF+or+Screenshot)  
*Replace the placeholder above with an actual GIF/screenshot of the app in action.*

---

## ✨ Features

- ✅ Real‑time webcam capture (OpenCV)  
- ✅ Peace‑sign detection using MediaPipe Hand Landmarker  
- ✅ Automatic background blur when the gesture is held  
- ✅ Sound effect playback via **ffplay** (FFmpeg)  
- ✅ Pink‑love emoji border overlay (transparent PNG)  
- ✅ Cross‑platform: Windows, Linux, macOS (untested on macOS)  
- ✅ Beginner‑friendly setup with a single `requirements.txt`  

---

## 🛠️ Tech Stack

| Component | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **OpenCV (`opencv-python`)** | Webcam access, image processing, display |
| **MediaPipe** | Hand landmark detection |
| **NumPy** | Array operations (used internally by OpenCV/MediaPipe) |
| **FFmpeg/ffplay** | Audio playback (no extra Python audio dependency) |
| **Pillow** (optional) | Generates a placeholder emoji if `love_pink.png` is missing |

---

## 📦 Prerequisites

- **Python** ≥ 3.10  
- A working **webcam** (`/dev/video0` on Linux, default camera on Windows/macOS)  
- **FFmpeg** installed (provides the `ffplay` command)  

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/moezaonlyone/foto-kita-blur.git
cd foto-kita-blur
```

### 2️⃣ Create an isolated virtual environment (recommended)

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Ensure **ffplay** is available

| OS | Command |
|----|---------|
| **Ubuntu / Debian** | `sudo apt-get update && sudo apt-get install -y ffmpeg` |
| **Fedora** | `sudo dnf install -y ffmpeg` |
| **macOS (Homebrew)** | `brew install ffmpeg` |
| **Windows** | Download the FFmpeg binary from <https://ffmpeg.org/download.html>, extract, and add the `bin` folder to your `PATH`. |

You can verify the installation with:

```bash
ffplay -version
```

### 5️⃣ Run the demo

```bash
python blur.py
```

---

## 📖 Usage

1. Launch the program: `python blur.py`.  
2. Show a **peace sign** (index + middle finger up, ring & pinky down) to:
   - Blur the camera feed  
   - Play the sound effect (`assets/sound-foto-kita-blur.mp3`)  
   - Draw a border of tiny pink‑love emojis around the screen edges  
3. Press **Esc** or **`q`** to quit the application.

---

## 📁 Project Structure

```
foto-kita-blur/
│
├── assets/
│   ├── love_pink.png          # Transparent pink‑love emoji (PNG)
│   └── sound-foto-kita-blur.mp3
│
├── models/
│   └── hand_landmarker.task   # MediaPipe Hand Landmarker model (~7.5 MB)
│
├── blur.py                    # Main script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
└── .gitignore                 # Files/folders ignored by Git
```

---

## 📜 License

This project is released under the **MIT License** – see the [`LICENSE`](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **MediaPipe Hand Landmarker** (Google) – for robust hand detection.  
- **OpenCV (`opencv-python`)** – for webcam handling and image processing.  
- **NumPy** – fundamental array library used by OpenCV/MediaPipe.  
- **FFmpeg/ffplay** – lightweight audio playback.  

---

## 🐞 Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'cv2'` | OpenCV not installed | Run `pip install -r requirements.txt` (or `pip install opencv-python`) |
| `FileNotFoundError: Missing MediaPipe model: …/hand_landmarker.task` | Model file missing or wrong path | Verify `models/hand_landmarker.task` exists relative to `blur.py` |
| `No module named 'PIL'` (only when generating placeholder) | Pillow not installed (optional) | Install with `pip install pillow` – needed only for auto‑generated emoji |
| `qt.qpa.plugin: Could not find the Qt platform plugin "wayland"` | Informational warning on Linux Wayland sessions | Does **not** stop the app; webcam window should still appear. Install a Qt platform plugin (`sudo apt-get install qt5-wayland`) or run with `xvfb-run -a python blur.py` to silence it. |
| No sound plays, but you see `[DEBUG] Starting sound…` | MP3 missing or `ffplay` not in PATH | Check that `assets/sound-foto-kita-blur.mp3` exists and run `which ffplay`. Install FFmpeg if needed. |
| Emoji border not visible | Emoji PNG missing or invalid | Ensure `assets/love_pink.png` exists and is a valid PNG with transparency. The script will create a placeholder if absent, but a custom image looks better. |
| Webcam shows black / no frames | Camera not accessible or already in use | Close other apps using the webcam, verify camera permissions, or try a different index (`cv2.VideoCapture(1)`). |
| Gesture not detected | Poor lighting, hand out of frame, or incorrect gesture | Ensure good lighting, keep hand fully visible, and make the peace sign (✌️). |

---

## ✅ Contributing

Feel free to open issues or submit pull requests if you’d like to improve the project (e.g., add more gestures, improve UI, or package as an executable).

---

*Happy coding!* 🚀💖📸  

---  

*Made with ❤️ by [moezaonlyone](https://github.com/moezaonlyone)*  
