"""
Suggested Kaggle datasets for helmet, triple ride, and lane violation.
Format: YOLO (images + labels with .txt) or we try to auto-detect structure.

Training dataset reference: https://codeshare.io/final
"""
TRAINING_DATASET_LINK = "https://codeshare.io/final"

# Notebook reference: https://www.kaggle.com/code/pkdarabi/helmet-violations/notebook
KAGGLE_PRESETS = {
    "helmet": [
        {
            "slug": "pkdarabi/helmet-violations",
            "name": "Helmet Violations (pkdarabi)",
            "task": "helmet",
            "description": "From notebook: motorcycle/scooter helmet violation detection. Notebook: kaggle.com/code/pkdarabi/helmet-violations",
        },
        {
            "slug": "abuzarkhaaan/helmetbehncode",
            "name": "Helmet Detection (YOLOv8)",
            "task": "helmet",
            "description": "Helmet / no-helmet on motorcycles",
        },
        {
            "slug": "andrewmvd/helmet-detection",
            "name": "Helmet Detection (Object Detection)",
            "task": "helmet",
            "description": "Images with helmet annotations",
        },
    ],
    "triple_ride": [
        {
            "slug": "advaitasen/ride-safety-dataset-of-mumbai-and-delhi",
            "name": "Ride Safety (Mumbai & Delhi)",
            "task": "triple_ride",
            "description": "Two-wheeler safety and overcrowding",
        },
        # If no dedicated triple-ride dataset, user can use custom or person+vehicle
        {
            "slug": "sshikamaru/coco-vehicle-person-bike",
            "name": "COCO Vehicle/Person/Bike (for custom triple-ride)",
            "task": "triple_ride",
            "description": "Use with person + motorcycle to infer triple ride",
        },
    ],
    "lane_violation": [
        {
            "slug": "muhammadrayanshahid/road-lane-detection-video-dataset",
            "name": "Road Lane Detection (Videos)",
            "task": "lane_violation",
            "description": "Lane lines; combine with vehicle detection for lane violation",
        },
        {
            "slug": "kumaresanmanickam/udacity-self-driving-car",
            "name": "Udacity Self-Driving (Lane + Vehicle)",
            "task": "lane_violation",
            "description": "Lane and vehicle data for autonomous driving",
        },
    ],
}


def get_all_presets():
    """Flat list of all presets for API."""
    out = []
    for task, presets in KAGGLE_PRESETS.items():
        for p in presets:
            out.append({**p})
    return out


def get_training_dataset_link():
    """Return the training dataset reference link."""
    return TRAINING_DATASET_LINK


def get_presets_for_task(task: str):
    return KAGGLE_PRESETS.get(task, [])
