"""
Train YOLO model using a Kaggle dataset. Runs in thread; updates training_state.
"""
import shutil
from pathlib import Path
from typing import Optional, List

from app.training_state import set_state
from app.model_config import WEIGHTS_DIR, set_custom_model


def _find_data_yaml(root: Path) -> Optional[Path]:
    for name in ("data.yaml", "dataset.yaml", "data.yml"):
        p = root / name
        if p.exists():
            return p
    # Check one level down (common: dataset/dataset/data.yaml)
    for sub in root.iterdir():
        if sub.is_dir():
            for name in ("data.yaml", "dataset.yaml"):
                p = sub / name
                if p.exists():
                    return p
    return None


def _find_train_val_dirs(root: Path):
    """Find train/val image dirs. Returns (train_images_path, val_images_path) or (None, None)."""
    # Try images/train, images/val
    img = root / "images"
    if img.exists():
        train = img / "train"
        val = img / "val"
        if train.exists() or val.exists():
            return (train if train.exists() else val), (val if val.exists() else train)
    # Try train/images, val/images
    train_img = root / "train" / "images"
    val_img = root / "val" / "images"
    if train_img.exists() or val_img.exists():
        return (train_img if train_img.exists() else val_img), (val_img if val_img.exists() else train_img)
    # Single folder
    for sub in root.iterdir():
        if sub.is_dir() and any(sub.glob("*.jpg")) or any(sub.glob("*.png")):
            return sub, sub
    return None, None


def _create_data_yaml(root: Path, train_dir: Path, val_dir: Path, class_names: List[str]) -> Path:
    """Create a data.yaml for Ultralytics in root."""
    # Labels assumed next to images with same structure: labels/train, labels/val
    train_labels = root / "labels" / "train" if (root / "labels" / "train").exists() else root / "train" / "labels"
    val_labels = root / "labels" / "val" if (root / "labels" / "val").exists() else root / "val" / "labels"
    if not train_labels.exists():
        train_labels = train_dir.parent / "labels" if (train_dir.parent / "labels").exists() else train_dir.parent
    if not val_labels.exists():
        val_labels = val_dir.parent / "labels" if (val_dir.parent / "labels").exists() else val_dir.parent

    nc = len(class_names) if class_names else 2
    names = class_names or ["class0", "class1"]
    path_str = str(root.resolve())
    # Relative to path
    train_rel = str(train_dir.relative_to(root)) if root in train_dir.parents or train_dir == root else "images/train"
    val_rel = str(val_dir.relative_to(root)) if root in val_dir.parents or val_dir == root else "images/val"
    yaml_content = f"""path: {path_str}
train: {train_rel}
val: {val_rel}
nc: {nc}
names: {names}
"""
    yaml_path = root / "data.yaml"
    yaml_path.write_text(yaml_content)
    return yaml_path


def run_training(task_type: str, kaggle_slug: str, epochs: int = 20):
    """
    Download dataset from Kaggle, prepare data.yaml, train YOLO, save to weights/.
    Updates training_state. Run from a background thread.
    """
    from app.kaggle_client import download_dataset, ensure_kaggle_credentials
    from ultralytics import YOLO

    set_state(status="running", task_type=task_type, kaggle_slug=kaggle_slug, total_epochs=epochs, message="Checking Kaggle credentials...")
    if not ensure_kaggle_credentials():
        set_state(status="failed", error="Kaggle credentials not found. Add ~/.kaggle/kaggle.json or set KAGGLE_USERNAME and KAGGLE_KEY.")
        return

    data_root = Path(__file__).resolve().parent.parent / "data" / "downloads"
    data_root.mkdir(parents=True, exist_ok=True)
    slug_safe = kaggle_slug.replace("/", "_")
    extract_path = data_root / slug_safe

    try:
        set_state(message="Downloading dataset from Kaggle...")
        dataset_path = download_dataset(kaggle_slug, str(extract_path.parent))
        # If download creates a new folder inside dest, use it
        if not dataset_path.exists():
            dataset_path = extract_path
        root = dataset_path if dataset_path.is_dir() else dataset_path.parent

        data_yaml = _find_data_yaml(root)
        if not data_yaml:
            train_dir, val_dir = _find_train_val_dirs(root)
            if train_dir is None:
                set_state(status="failed", error="Could not find train/val images. Dataset should have images/train, images/val or train/images, val/images.")
                return
            data_yaml = _create_data_yaml(root, train_dir, val_dir, [])
            # If dataset has existing names in a yaml elsewhere, we could read them
        set_state(message="Starting YOLO training...")

        model = YOLO("yolov8n.pt")
        results = model.train(
            data=str(data_yaml),
            epochs=epochs,
            imgsz=640,
            batch=16,
            exist_ok=True,
            project=str(Path(__file__).resolve().parent.parent / "runs"),
            name=task_type,
        )
        # best.pt is in runs/task_type/weights/best.pt
        runs_dir = Path(__file__).resolve().parent.parent / "runs" / task_type
        best_pt = runs_dir / "weights" / "best.pt"
        if not best_pt.exists():
            best_pt = runs_dir / "best.pt"
        if not best_pt.exists():
            set_state(status="failed", error="Training finished but best.pt not found.")
            return

        WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        dest_pt = WEIGHTS_DIR / f"{task_type}_best.pt"
        shutil.copy(best_pt, dest_pt)

        # Get class names from trained model
        trained = YOLO(str(dest_pt))
        class_names = list(trained.names.values()) if hasattr(trained, "names") and trained.names else []

        set_custom_model(str(dest_pt), class_names)
        set_state(
            status="completed",
            message=f"Training done. Model saved to {dest_pt.name}",
            current_epoch=epochs,
            error=None,
        )
    except Exception as e:
        set_state(status="failed", error=str(e))
