from pathlib import Path

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".m4v"}

def validate_video_path(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise ValueError("Video file does not exist.")
    if p.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported video format: {p.suffix}")
    if p.stat().st_size == 0:
        raise ValueError("Video file is empty.")
    return p
