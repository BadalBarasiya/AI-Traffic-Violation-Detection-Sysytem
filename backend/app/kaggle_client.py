"""
Download datasets from Kaggle. Requires Kaggle API credentials:
~/.kaggle/kaggle.json with {"username":"...", "key":"..."}
or env KAGGLE_USERNAME and KAGGLE_KEY.
"""
import os
from pathlib import Path


def download_dataset(kaggle_slug: str, dest_dir: str) -> Path:
    """
    Download a Kaggle dataset by slug (e.g. 'owner/dataset-name') into dest_dir.
    Returns path to the extracted dataset folder.
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        raise RuntimeError(
            "Kaggle API not installed. Run: pip install kaggle"
        )

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    # Kaggle downloads as zip; we download into dest then extract
    api = KaggleApi()
    api.authenticate()
    # dataset_download_files downloads and extracts by default into dest/dataset_slug
    parts = kaggle_slug.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Kaggle slug must be like 'owner/dataset-name'")
    api.dataset_download_files(kaggle_slug, path=str(dest), unzip=True)
    # After download, the folder is usually dest/<dataset-name> or dest has contents
    # List and return the first directory that has images/labels or train/val
    for item in dest.iterdir():
        if item.is_dir():
            return item
    return dest


def ensure_kaggle_credentials():
    """Check that Kaggle credentials exist."""
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    return kaggle_json.exists()
