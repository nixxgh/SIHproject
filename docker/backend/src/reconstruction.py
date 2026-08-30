import subprocess
from pathlib import Path

def run_colmap(image_dir: str, output_dir: str):
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)

    database_path = output_dir / "database.db"
    sparse_dir = output_dir / "sparse"
    sparse_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(["colmap", "feature_extractor", "--database_path", str(database_path), "--image_path", str(image_dir)], check=True)
    subprocess.run(["colmap", "exhaustive_matcher", "--database_path", str(database_path)], check=True)
    subprocess.run(["colmap", "mapper", "--database_path", str(database_path), "--image_path", str(image_dir), "--output_path", str(sparse_dir)], check=True)

def run_dense_reconstruction(image_dir: str, output_dir: str):
    output_dir = Path(output_dir)
    sparse_dir = output_dir / "sparse" / "0"
    dense_dir = output_dir / "dense"
    dense_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(["colmap", "image_undistorter", "--image_path", str(image_dir), "--input_path", str(sparse_dir), "--output_path", str(dense_dir), "--output_type", "COLMAP"], check=True)
    subprocess.run(["colmap", "patch_match_stereo", "--workspace_path", str(dense_dir), "--workspace_format", "COLMAP"], check=True)
    subprocess.run(["colmap", "stereo_fusion", "--workspace_path", str(dense_dir), "--workspace_format", "COLMAP", "--output_path", str(dense_dir / "fused.ply")], check=True)
