import shutil
import subprocess
import os
from pathlib import Path
import cv2

PRESETS = {
    "low": {"width": 1280, "height": 720, "fps": 5},
    "high": {"width": None, "height": None, "fps": 20},
}

def extract_frames(video_path: str, output_dir: str, preset: str = "low") -> int:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}. Use 'low' or 'high'.")

    settings = PRESETS[preset]
    output_path = Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # --- UPGRADED: Transcode ANY format to standard H.264 ---
    # Safely swap the original extension (.mov, .avi) with _h264.mp4
    base_name = os.path.splitext(video_path)[0]
    normalized_video = f"{base_name}_h264.mp4"
    
    print(f"[*] Transcoding {video_path} to standard H.264...")
    
    # -preset fast: Speeds up the conversion for the hackathon
    # -an: Strips the audio track completely (SfM doesn't need it, saves time/space)
    # -pix_fmt yuv420p: Forces standard 8-bit color for max OpenCV compatibility
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, 
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an",
        normalized_video
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(normalized_video):
         raise RuntimeError(f"[!] FFmpeg failed to transcode {video_path}. Is the file corrupted?")
    # --------------------------------------------------------

    cap = cv2.VideoCapture(normalized_video) # Read the cleanly converted H.264 video
    if not cap.isOpened():
        raise ValueError(f"Could not open transcoded video: {normalized_video}")

    original_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(1, round(original_fps / settings["fps"]))

    frame_index = 0
    saved_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_index % frame_interval == 0:
            if settings["width"] and settings["height"]:
                frame = cv2.resize(frame, (settings["width"], settings["height"]))

            frame_path = output_path / f"frame_{saved_count:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            saved_count += 1

        frame_index += 1

    cap.release()
    
    # Cleanup the temporary H.264 video so it doesn't waste server space
    if os.path.exists(normalized_video):
        os.remove(normalized_video)

    return saved_count
