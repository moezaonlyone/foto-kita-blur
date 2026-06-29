import subprocess
from pathlib import Path

sound_path = Path(__file__).parent.parent / "assets" / "sound-foto-kita-blur.mp3"
print(f"Playing sound from: {sound_path}")
try:
    if not sound_path.exists():
        print("Error: Sound file not found.")
    else:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", str(sound_path)])
        print("Done")
except Exception as e:
    print(f"Error: {e}")
