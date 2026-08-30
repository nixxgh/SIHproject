import shutil
from pathlib import Path
import cv2

def frame_score(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    orb = cv2.ORB_create(nfeatures=1000)
    keypoints, _ = orb.detectAndCompute(gray, None)
    features = len(keypoints) if keypoints is not None else 0
    brightness = gray.mean()

    return sharpness, features, brightness

def is_similar(frame1, frame2, threshold=0.69):
    gray1 = cv2.resize(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), (64, 64))
    gray2 = cv2.resize(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY), (64, 64))
    similarity = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
    return similarity >= threshold

def select_frames(input_dir: str, output_dir: str, max_frames: int = 150):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    selected = []
    last_frame = None

    for frame_path in sorted(input_path.glob("*.jpg")):
        frame = cv2.imread(str(frame_path))
        if frame is None:
            continue

        sharpness, features, brightness = frame_score(frame)

        if sharpness < 40 or features < 100 or brightness < 30 or brightness > 225:
            continue

        if last_frame is not None and is_similar(frame, last_frame):
            continue

        selected.append((frame_path, frame))
        last_frame = frame

    for frame_path, frame in selected:
        cv2.imwrite(str(output_path / frame_path.name), frame)

    return len(selected)
