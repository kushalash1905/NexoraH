"""Script to download and cache sentence-transformers/all-MiniLM-L6-v2 offline.

Must be executed before the hackathon while an internet connection is available.
Runtime execution strictly prohibits downloading or internet calls.
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer


def download_and_save_model():
    base_dir = Path(__file__).resolve().parent.parent
    target_dir = base_dir / "models" / "all-MiniLM-L6-v2"

    print(f"Target directory: {target_dir}")
    if target_dir.exists() and (target_dir / "model.safetensors").exists():
        print("Model is already downloaded and cached locally!")
        return

    print("Downloading 'sentence-transformers/all-MiniLM-L6-v2'...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(target_dir))
    print(f"Model successfully saved to {target_dir}")


if __name__ == "__main__":
    download_and_save_model()
