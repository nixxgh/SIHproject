from fastapi import FastAPI

app = FastAPI(title="NTRO 3D Reconstruction API")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Backend engine is running and ready for SfM pipeline."
    }
