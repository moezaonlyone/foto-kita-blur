#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Peace‑Blur + Sound + Pink Love Emoji border

- Detects a peace sign (index + middle finger up, ring & pinky down)
  using MediaPipe Hand Landmarker.
- When the gesture is seen:
    * The camera frame is blurred.
    * The sound effect (sound-foto-kita-blur.mp3) starts playing.
    * A border of tiny pink love emojis is drawn around the screen.
- When the gesture disappears:
    * The blur is removed.
    * The sound stops.
- Press ESC or 'q' to quit.
"""

import os
import subprocess
import time
from pathlib import Path
from time import monotonic

import cv2
import mediapipe as mp
import numpy as np

# ----------------------------------------------------------------------
# Paths & constants
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "models" / "hand_landmarker.task"
SOUND_PATH = BASE_DIR / "assets" / "sound-foto-kita-blur.mp3"
EMOJI_PATH = BASE_DIR / "assets" / "love_pink.png"


# ----------------------------------------------------------------------
# MediaPipe helpers
# ----------------------------------------------------------------------
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def finger_up(tip: int, pip: int, landmarks) -> bool:
    """True if fingertip is above the pip joint (smaller y)."""
    return landmarks[tip].y < landmarks[pip].y


def is_peace(landmarks) -> bool:
    """Peace sign = index & middle up, ring & pinky down."""
    return (
        finger_up(8, 6, landmarks)  # index tip > pip
        and finger_up(12, 10, landmarks)  # middle tip > pip
        and not finger_up(16, 14, landmarks)  # ring down
        and not finger_up(20, 18, landmarks)  # pinky down
    )


def create_landmarker() -> HandLandmarker:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing MediaPipe model: {MODEL_PATH}")

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.1,
        min_hand_presence_confidence=0.1,
        min_tracking_confidence=0.1,
    )
    return HandLandmarker.create_from_options(options)


# ----------------------------------------------------------------------
# Audio helper – ffplay subprocess
# ----------------------------------------------------------------------
def start_sound() -> subprocess.Popen | None:
    """Launch ffplay to play the MP3 silently (looped); return the Popen object."""
    if not SOUND_PATH.is_file():
        print(f"[WARN] Sound file not found: {SOUND_PATH}", flush=True)
        return None
    try:
        # -loop 0 → repeat indefinitely until we kill the process
        return subprocess.Popen(
            ["ffplay", "-nodisp", "-loop", "0", str(SOUND_PATH)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[ERROR] Failed to start ffplay: {e}", flush=True)
        return None


def stop_sound(proc: subprocess.Popen | None):
    """Terminate the ffplay subprocess gracefully."""
    if proc is None:
        return
    # Only attempt to terminate if the process is still alive
    if proc.poll() is None:  # None means still running
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    # If it already exited, we simply drop the reference


# ----------------------------------------------------------------------
# Emoji handling (load + drawing)
# ----------------------------------------------------------------------
def load_emoji() -> tuple[np.ndarray, np.ndarray] | None:
    """
    Load the emoji PNG with transparency.
    Returns (color_image, alpha_mask) where alpha_mask is in range [0,1].
    If the file is missing we try to generate a simple pink heart.
    """
    if EMOJI_PATH.is_file():
        img = cv2.imread(str(EMOJI_PATH), cv2.IMREAD_UNCHANGED)  # BGRA
        if img is not None and img.shape[2] == 4:
            bgr = img[:, :, :3]
            alpha = img[:, :, 3] / 255.0
            return bgr, alpha
        else:
            print(f"[WARN] {EMOJI_PATH} is not a valid BGRA image", flush=True)
    else:
        print(
            f"[WARN] Emoji file not found: {EMOJI_PATH} – generating a placeholder",
            flush=True,
        )

    # ------- fallback: generate a tiny pink heart with Pillow -------
    try:
        from PIL import Image, ImageDraw  # Pillow is lightweight; install if missing
    except Exception as e:
        print(
            f"[ERROR] Pillow not installed – cannot generate fallback emoji: {e}",
            flush=True,
        )
        return None

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Simple heart shape (two circles + a triangle)
    r = 20
    left = 16
    top = 16
    draw.ellipse(
        (left, top, left + 2 * r, top + 2 * r), fill=(255, 105, 180, 255)
    )  # left circle
    draw.ellipse(
        (left + r, top, left + 3 * r, top + 2 * r), fill=(255, 105, 180, 255)
    )  # right circle
    draw.polygon(
        [(left, top + r), (left + 2 * r, top + 2 * r + r), (left + 3 * r, top + r)],
        fill=(255, 105, 180, 255),
    )
    # Save for future runs
    img.save(str(EMOJI_PATH))
    print(f"[INFO] Generated placeholder emoji at {EMOJI_PATH}", flush=True)

    bgr = np.array(img)[:, :, :3][:, :, ::-1].copy()  # RGB → BGR for OpenCV
    alpha = np.array(img)[:, :, 3] / 255.0
    return bgr, alpha


def draw_border_emojis(
    frame: np.ndarray,
    emoji_bgr: np.ndarray,
    emoji_alpha: np.ndarray,
    scale: float = 0.07,
    spacing: int = 8,
):
    """
    Tile the emoji along the four borders of `frame`.
    - `scale`: size of emoji relative to original PNG (0.0~1.0)
    - `spacing`: pixel gap between consecutive emojis
    """
    h, w = emoji_bgr.shape[:2]
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    # Pre‑scale once – cheaper than resizing per tile
    small_bgr = cv2.resize(emoji_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    small_alpha = cv2.resize(emoji_alpha, (new_w, new_h), interpolation=cv2.INTER_AREA)

    f_h, f_w = frame.shape[:2]

    # ----- Top edge -----
    x = 0
    while x + new_w <= f_w:
        y1, y2 = 0, new_h
        x1, x2 = x, x + new_w
        _alpha_blend(frame, small_bgr, small_alpha, x1, y1, x2, y2)
        x += new_w + spacing

    # ----- Bottom edge -----
    x = 0
    while x + new_w <= f_w:
        y1, y2 = f_h - new_h, f_h
        x1, x2 = x, x + new_w
        _alpha_blend(frame, small_bgr, small_alpha, x1, y1, x2, y2)
        x += new_w + spacing

    # ----- Left edge (skip corners already drawn) -----
    y = new_h + spacing
    while y + new_h <= f_h - new_h - spacing:
        x1, x2 = 0, new_w
        y1, y2 = y, y + new_h
        _alpha_blend(frame, small_bgr, small_alpha, x1, y1, x2, y2)
        y += new_h + spacing

    # ----- Right edge -----
    y = new_h + spacing
    while y + new_h <= f_h - new_h - spacing:
        x1, x2 = f_w - new_w, f_w
        y1, y2 = y, y + new_h
        _alpha_blend(frame, small_bgr, small_alpha, x1, y1, x2, y2)
        y += new_h + spacing


def _alpha_blend(
    dst: np.ndarray,
    src_bgr: np.ndarray,
    src_alpha: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
):
    """Blend src onto dst[y1:y2, x1:x2] using src_alpha (0‑1)."""
    for c in range(3):  # B, G, R
        dst[y1:y2, x1:x2, c] = (
            src_alpha * src_bgr[:, :, c] + (1 - src_alpha) * dst[y1:y2, x1:x2, c]
        )


# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera 0")

    # Optional: lower resolution to reduce CPU load
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Load (or generate) emoji once
    emoji_data = load_emoji()  # (bgr, alpha) or None

    start_time = monotonic()
    last_timestamp_ms = -1
    sound_proc = None
    sound_playing = False

    # Create landmarker once
    landmarker = create_landmarker()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Frame not received – exiting loop", flush=True)
                break

            # Mirror the image (selfie view)
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            timestamp_ms = int((monotonic() - start_time) * 1000)
            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1
            last_timestamp_ms = timestamp_ms

            # Hand detection
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            hand_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            num_hands = len(hand_result.hand_landmarks)
            if num_hands > 0:
                print(f"[DEBUG] Detected {num_hands} hand(s)", flush=True)

            peace_detected = any(
                is_peace(hand_landmarks)
                for hand_landmarks in hand_result.hand_landmarks
            )

            # ------------------------------------------------------------------
            # Visual feedback: blur + sound + emoji border
            # ------------------------------------------------------------------
            if peace_detected:
                print("[DEBUG] Peace detected!", flush=True)
                frame = cv2.GaussianBlur(frame, (61, 61), 0)

                # Start sound if not already playing
                if not sound_playing:
                    print("[DEBUG] Starting sound...", flush=True)
                    sound_proc = start_sound()
                    if sound_proc is not None:
                        sound_playing = True

                # Draw emoji border if we have an emoji image
                if emoji_data is not None:
                    emoji_bgr, emoji_alpha = emoji_data
                    draw_border_emojis(
                        frame, emoji_bgr, emoji_alpha, scale=0.07, spacing=6
                    )
            else:
                # Stop sound if it was playing
                if sound_playing:
                    print("[DEBUG] Stopping sound...", flush=True)
                    stop_sound(sound_proc)
                    sound_proc = None
                    sound_playing = False

            # Show the frame
            cv2.imshow("Peace Blur", frame)

            # ------------------------------------------------------------------
            # Exit handling
            # ------------------------------------------------------------------
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):  # ESC or 'q'
                print("[INFO] Exit requested by user", flush=True)
                break
            # Small sleep to cap loop (~200 fps max)
            time.sleep(0.005)

    finally:
        # Clean‑up everything
        if sound_playing and sound_proc:
            stop_sound(sound_proc)
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Resources released – goodbye!", flush=True)


if __name__ == "__main__":
    main()
