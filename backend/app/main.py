from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import asyncio
import random
import threading
import numpy as np
from datetime import datetime, timezone

from app.detector import YOLODetector
from app.violation_logic import check_violations, check_image_upload_violations
from app.websocket_manager import ConnectionManager
from app.model_config import get_model_path, get_class_names
from app.training_state import get_state, set_state
from app.dataset_presets import get_all_presets, get_presets_for_task, get_training_dataset_link
from app.trainer import run_training

app = FastAPI()
manager = ConnectionManager()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_detector():
    path = get_model_path()
    names = get_class_names()
    return YOLODetector(path, class_names=names)


# Load YOLO model at startup (custom if trained, else default)
detector = _load_detector()


def _warmup_detector():
    """Run a dummy inference so first real request is fast."""
    try:
        dummy = np.zeros((224, 224, 3), dtype=np.uint8)
        detector.detect(dummy, imgsz=224)
        print("Model warmup done.")
    except Exception as e:
        print("Warmup skipped:", e)


threading.Thread(target=_warmup_detector, daemon=True).start()

LOCATIONS = ["SG Highway", "CG Road", "Ashram Road", "Ring Road", "Satellite", "Paldi"]
VEHICLE_PREFIXES = ["GJ-01-AB", "GJ-05-CD", "GJ-27-EF", "GJ-18-GH"]
FINES = {
    "Triple Riding": 2000,
    "No Helmet": 1000,
    "Helmet Violation": 1000,
    "Wrong Way Driving": 3000,
    "Person Detected": 500,
    "Lane Violation": 1500,
}

VIOLATIONS_DIR = Path(__file__).resolve().parent.parent / "violations"
VIOLATIONS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/violations", StaticFiles(directory=str(VIOLATIONS_DIR)), name="violations")


def _build_violation_payload(violation_type: str):
    """Build violation payload for broadcast/response."""
    return {
        "id": f"V{random.randint(1000, 9999)}",
        "type": violation_type,
        "vehicle": f"{random.choice(VEHICLE_PREFIXES)}-{random.randint(1000, 9999)}",
        "speed": "-",
        "time": datetime.now().strftime("%I:%M %p"),
        "location": random.choice(LOCATIONS),
        "fine": FINES.get(violation_type, 500),
        "status": "Pending",
    }


@app.websocket("/ws/violations")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("WebSocket Connected")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


    if not cap.isOpened():
        print("Error: Could not open webcam")
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                await asyncio.sleep(0.5)
                continue

            # Run YOLO detection
            detections = detector.detect(frame)

            # Check violation logic
            violations = check_violations(detections)

            # Send violations if any
            for v in violations:
                violation_type = v.get("type", "Unknown")
                violation_data = _build_violation_payload(violation_type)
                print("Sending violation:", violation_data)
                await manager.broadcast(violation_data)

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("WebSocket Disconnected")
        manager.disconnect(websocket)

    except Exception as e:
        print("Loop Error:", e)

    finally:
        cap.release()
        print("Camera Released")


# ---------- Manual Image Upload: POST /detect/image ----------


def _get_vehicle_number_from_ocr(_image) -> str:
    """Placeholder for future OCR. Returns UNKNOWN for now."""
    return "UNKNOWN"


@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """
    Upload traffic image for violation detection.
    Returns: vehicle_number, violation_type (Helmet Violation | Triple Riding | None), confidence, timestamp.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (e.g. image/jpeg, image/png).")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Use JPEG or PNG.")

    # Reject extremely large images to avoid very slow CPU inference
    h, w = frame.shape[:2]
    if max(h, w) > 2000:
        raise HTTPException(
            status_code=413,
            detail="Image too large for real-time detection. Please upload a resized image (e.g. <= 1280x720).",
        )

    # Resize large images to speed up inference
    max_size = 256
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

    loop = asyncio.get_event_loop()
    try:
        detections = await loop.run_in_executor(None, lambda: detector.detect(frame, imgsz=224))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")

    violation_type, confidence = check_image_upload_violations(detections)
    vehicle_number = _get_vehicle_number_from_ocr(frame)

    # Generate fine and store image when violation detected
    fine = FINES.get(violation_type, 0) if violation_type != "None" else 0
    image_url = None

    if violation_type != "None":
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        ext = "jpg" if file.content_type and "jpeg" in file.content_type else "png"
        filename = f"violation_{ts}_{random.randint(1000, 9999)}.{ext}"
        filepath = VIOLATIONS_DIR / filename
        filepath.write_bytes(contents)
        image_url = f"/violations/{filename}"

    return {
        "vehicle_number": vehicle_number,
        "violation_type": violation_type,
        "confidence": confidence,
        "fine": fine,
        "image_url": image_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------- Upload image for detection (adds to violations & fines) ----------


@app.post("/api/detect")
async def api_detect_upload(file: UploadFile = File(...)):
    """
    Upload a violation photo. Runs detection, adds any violations to Recent Violations
    and Fines Generated (via WebSocket broadcast). Returns detection result.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (e.g. image/jpeg, image/png).")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Use JPEG or PNG.")
    detections = detector.detect(frame)
    violations = check_violations(detections)
    result_violations = []
    for v in violations:
        violation_type = v.get("type", "Unknown")
        payload = _build_violation_payload(violation_type)
        await manager.broadcast(payload)
        result_violations.append(payload)
    return {
        "detections_count": len(detections),
        "violations_count": len(violations),
        "violations": result_violations,
        "message": f"Detected {len(detections)} objects, {len(violations)} violation(s). Added to Recent Violations and Fines."
    }


# ---------- Training API (user input: Kaggle data, train model) ----------

class TrainRequest(BaseModel):
    task_type: str  # helmet | triple_ride | lane_violation
    kaggle_slug: str  # e.g. "owner/dataset-name"
    epochs: int = 20


@app.get("/api/datasets")
def api_datasets(task: str = None):
    """List suggested Kaggle datasets. Optional ?task=helmet|triple_ride|lane_violation."""
    if task:
        return get_presets_for_task(task)
    return get_all_presets()


@app.get("/api/training-dataset-link")
def api_training_dataset_link():
    """Return the training dataset reference link (codeshare)."""
    return {"link": get_training_dataset_link()}


@app.get("/api/training/status")
def api_training_status():
    """Current training job status."""
    s = get_state()
    return {
        "status": s.status,
        "task_type": s.task_type,
        "kaggle_slug": s.kaggle_slug,
        "current_epoch": s.current_epoch,
        "total_epochs": s.total_epochs,
        "message": s.message,
        "error": s.error,
        "best_metric": s.best_metric,
    }


@app.post("/api/train")
def api_start_training(req: TrainRequest):
    """Start training in background. Requires Kaggle credentials."""
    s = get_state()
    if s.status == "running":
        raise HTTPException(status_code=409, detail="Training already in progress.")
    if req.epochs < 1 or req.epochs > 200:
        raise HTTPException(status_code=400, detail="epochs must be 1–200.")
    task = req.task_type.lower()
    if task not in ("helmet", "triple_ride", "lane_violation"):
        raise HTTPException(status_code=400, detail="task_type must be helmet, triple_ride, or lane_violation.")

    def run():
        run_training(task_type=task, kaggle_slug=req.kaggle_slug.strip(), epochs=req.epochs)

    threading.Thread(target=run, daemon=True).start()
    return {"message": "Training started.", "task_type": task, "kaggle_slug": req.kaggle_slug}


@app.post("/api/model/reload")
def api_reload_model():
    """Reload detector from current model_config (e.g. after training)."""
    global detector
    detector.reload()
    return {"message": "Model reloaded.", "model_path": get_model_path()}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

# from fastapi import FastAPI, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# import cv2
# import asyncio
# import random
# from datetime import datetime

# from app.detector import YOLODetector
# from app.violation_logic import check_violations
# from app.websocket_manager import ConnectionManager

# app = FastAPI()
# manager = ConnectionManager()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# detector = YOLODetector("yolov8n.pt")


# @app.websocket("/ws/violations")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)

#     cap = cv2.VideoCapture(0)

#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             detections = detector.detect(frame)
#             violations = check_violations(detections)

#             for v in violations:
#                 violation_data = {
# "id": f"V{random.randint(1000,9999)}",
#     "type": "No Helmet",
#     "vehicle": f"GJ-01-AB-{random.randint(1000,9999)}",
#     "speed": "-",
#     "time": datetime.now().strftime("%I:%M %p"),
#     "location": "SG Highway",
#     "status": "Pending"
#                 }

#                 await manager.broadcast(violation_data)

#             await asyncio.sleep(0.2)

#     except:
#         manager.disconnect(websocket)

# # from fastapi import FastAPI, WebSocket
# # from fastapi.middleware.cors import CORSMiddleware
# # import cv2
# # import asyncio

# # from app.detector import YOLODetector
# # from app.violation_logic import check_violations
# # from app.websocket_manager import ConnectionManager

# # app = FastAPI()
# # manager = ConnectionManager()

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # detector = YOLODetector("yolov8n.pt")

# # @app.websocket("/ws/violations")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await manager.connect(websocket)

# #     cap = cv2.VideoCapture(0)  # webcam

# #     try:
# #         while True:
# #             ret, frame = cap.read()
# #             if not ret:
# #                 break

# #             detections = detector.detect(frame)
# #             violations = check_violations(detections)

# #             for v in violations:
# #                 await manager.broadcast(v)

# #             await asyncio.sleep(0.1)

# #     except:
# #         manager.disconnect(websocket)
# # _______________________________________________