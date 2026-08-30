import shutil
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

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

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
    return saved_count
