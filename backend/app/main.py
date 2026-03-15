from pathlib import Path
import base64
import json
import hmac
import hashlib
import os
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import asyncio
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from datetime import datetime, timezone

# Dedicated thread pool for YOLO inference (avoids blocking other async work)
INFERENCE_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="inference")
INFERENCE_TIMEOUT_SEC = 45

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


# ---------- Simple auth (admin & user roles) ----------

AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-me-in-production")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class CurrentUser(BaseModel):
    username: str
    role: str


# Demo users – replace with real DB in production.
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _create_token(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(AUTH_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def _decode_token(token: str) -> dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format.")
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(AUTH_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual_sig = _b64url_decode(sig_b64)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(status_code=401, detail="Invalid token signature.")
    payload_bytes = _b64url_decode(payload_b64)
    try:
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload.")


async def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.split(" ", 1)[1]
    payload = _decode_token(token)
    username = payload.get("sub")
    role = payload.get("role", "user")
    user = USERS_DB.get(username or "")
    if not user or user.get("role") != role:
        raise HTTPException(status_code=401, detail="Invalid user.")
    return CurrentUser(username=username, role=role)


async def get_current_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = USERS_DB.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    token = _create_token({"sub": req.username, "role": user["role"]})
    return TokenResponse(access_token=token, username=req.username, role=user["role"])


@app.get("/api/auth/me", response_model=CurrentUser)
async def auth_me(current: CurrentUser = Depends(get_current_user)):
    return current


@app.get("/api/admin/ping")
async def admin_ping(admin: CurrentUser = Depends(get_current_admin)):
    return {"message": "ok", "username": admin.username, "role": admin.role}


def _load_detector():
    path = get_model_path()
    names = get_class_names()
    return YOLODetector(path, class_names=names)


# Load YOLO model at startup (custom if trained, else default)
detector = _load_detector()


def _warmup_detector():
    """Run a dummy inference in the inference pool so first upload is fast."""
    try:
        dummy = np.zeros((320, 320, 3), dtype=np.uint8)
        detector.detect(dummy, imgsz=320)
        print("Model warmup done.")
    except Exception as e:
        print("Warmup skipped:", e)


# Warm up model in the same executor used for requests
INFERENCE_EXECUTOR.submit(_warmup_detector)

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

    loop = asyncio.get_event_loop()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                await asyncio.sleep(0.5)
                continue

            # Run YOLO detection in dedicated thread pool (imgsz=320 for speed)
            detections = await loop.run_in_executor(
                INFERENCE_EXECUTOR, lambda f=frame: detector.detect(f, imgsz=320)
            )

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


def _random_plate() -> str:
    """Return a random plate number (e.g. GJ-01-AB-1234). Used when OCR is not available or fails."""
    return f"{random.choice(VEHICLE_PREFIXES)}-{random.randint(1000, 9999)}"


def _get_vehicle_number_from_ocr(_image) -> str:
    """Placeholder for future OCR. Returns UNKNOWN for now; caller should use _random_plate() as fallback."""
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

    # Aggressive resize for fast CPU inference (small image = fast analysis)
    max_size = 256
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

    loop = asyncio.get_event_loop()
    try:
        detections = await asyncio.wait_for(
            loop.run_in_executor(INFERENCE_EXECUTOR, lambda: detector.detect(frame, imgsz=192)),
            timeout=INFERENCE_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=503,
            detail="Analysis took too long. Try a smaller image (e.g. under 800px) or try again.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")

    violation_type, confidence = check_image_upload_violations(detections)
    vehicle_number = _get_vehicle_number_from_ocr(frame)
    if not vehicle_number or vehicle_number == "UNKNOWN":
        vehicle_number = _random_plate()

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

    location = random.choice(LOCATIONS) if violation_type != "None" else None

    return {
        "vehicle_number": vehicle_number,
        "violation_type": violation_type,
        "confidence": confidence,
        "fine": fine,
        "image_url": image_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
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
    # Resize large images for faster inference
    h, w = frame.shape[:2]
    max_size = 320
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    loop = asyncio.get_event_loop()
    try:
        detections = await asyncio.wait_for(
            loop.run_in_executor(INFERENCE_EXECUTOR, lambda: detector.detect(frame, imgsz=256)),
            timeout=INFERENCE_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=503,
            detail="Analysis took too long. Try a smaller image or try again.",
        )
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
    import uvicorn # pyright: ignore[reportMissingImports]
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