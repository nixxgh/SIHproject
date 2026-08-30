import os
import shutil
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.responses import RedirectResponse

# Updated module imports to match package path
from src.frames import extract_frames
from src.selection import select_frames
from src.reconstruction import run_colmap, run_dense_reconstruction

app = FastAPI(title="Edge Station 3D Pipeline")

# Docker path configurations
INPUT_DIR = "/app/data/inputs"
OUTPUT_BASE = "/app/data/outputs"
ALL_FRAMES_DIR = f"{OUTPUT_BASE}/frames/all"
SELECTED_FRAMES_DIR = f"{OUTPUT_BASE}/frames/selected"
RECON_DIR = f"{OUTPUT_BASE}/reconstruction"

# Ensure directories exist before saving uploads
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_BASE, exist_ok=True)

def execute_pipeline(video_path: str, preset: str, max_frames: int):
    """The master function that runs asynchronously in the background."""
    try:
        print(f"[*] Starting background pipeline for {video_path}")
        extract_frames(video_path, ALL_FRAMES_DIR, preset=preset)
        select_frames(ALL_FRAMES_DIR, SELECTED_FRAMES_DIR, max_frames=max_frames)
        run_colmap(SELECTED_FRAMES_DIR, RECON_DIR)
        run_dense_reconstruction(SELECTED_FRAMES_DIR, RECON_DIR)
        print("[+] Pipeline completed successfully.")
    except Exception as e:
        print(f"[!] Pipeline failed: {str(e)}")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/api/v1/process")
async def trigger_processing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    preset: str = Form("low"),
    max_frames: int = Form(150),
):
    # Reject non-video uploads
    if not file.filename.endswith(('.mp4', '.mov', '.mkv', '.avi')):
        raise HTTPException(status_code=400, detail="Only video files are supported.")

    video_path = os.path.join(INPUT_DIR, file.filename)
    
    # Save the uploaded file to disk
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Hand the heavy lifting off to a background thread
    background_tasks.add_task(
        execute_pipeline, 
        video_path, 
        preset, 
        max_frames
    )
    
    return {
        "status": "processing_started",
        "filename": file.filename,
        "message": f"Pipeline triggered for {file.filename}.",
        "outputs_will_save_to": RECON_DIR
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "online", "service": "Reconstruction Engine"}
