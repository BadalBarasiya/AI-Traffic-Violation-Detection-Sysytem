# Traffic Dashboard

AI-powered **Traffic Violation Detection** system: a **backend** that captures webcam feed, runs YOLO object detection, detects violations, and streams them in real time to a **React dashboard** over WebSocket.

---

## Project structure

```
traffic-dashboard/
├── backend/                 # FastAPI + YOLO backend
│   ├── app/
│   │   ├── main.py          # FastAPI app, WebSocket, training API
│   │   ├── detector.py      # YOLO detector (default or custom from weights/)
│   │   ├── violation_logic.py # Maps class names to violation types
│   │   ├── websocket_manager.py
│   │   ├── kaggle_client.py # Download datasets from Kaggle
│   │   ├── trainer.py       # Run YOLO training in background
│   │   ├── dataset_presets.py # Suggested Kaggle datasets per task
│   │   ├── model_config.py  # Current model path and class names
│   │   └── training_state.py # Training job status
│   └── requirements.txt
├── src/                     # React (Vite) frontend
│   ├── App.jsx
│   ├── hooks/
│   │   └── useViolationsSocket.js  # WebSocket hook → backend /ws/violations
│   └── components/
│       ├── TrafficViolationUI.jsx  # Dashboard + Train model section
│       ├── TrainModel.jsx           # Task/dataset/epochs form, status, reload
│       └── dashboard/Header.jsx
├── .env.example             # Optional: VITE_WS_VIOLATIONS_URL
└── README.md
```

---

## How backend and frontend connect

1. **Backend** (FastAPI) runs on **port 8000** and exposes:
   - **WebSocket:** `ws://127.0.0.1:8000/ws/violations`
2. **Frontend** (Vite) runs on **port 5173** and:
   - Opens a WebSocket to the URL above (or `VITE_WS_VIOLATIONS_URL` if set).
   - Receives violation objects (id, type, vehicle, time, location, fine, status) and shows them in the dashboard.

The frontend also calls the **REST API** for **training** (see below). Set `VITE_API_URL` (default `http://localhost:8000`) if your backend runs elsewhere.

---

## Backend (Python)

- **Stack:** FastAPI, OpenCV (webcam), Ultralytics YOLO.
- **Flow:**
  1. Client connects to `GET /ws/violations` (WebSocket).
  2. Backend opens the default webcam (`cv2.VideoCapture(0)`).
  3. Each frame is run through YOLO; `violation_logic.check_violations(detections)` decides if there is a violation (e.g. person → "Person Detected").
  4. For each violation it builds a payload (id, type, vehicle, time, location, fine, status) and **broadcasts** it to all connected WebSocket clients.
- **Files:**
  - `main.py`: CORS, WebSocket endpoint, camera loop, violation broadcast.
  - `detector.py`: Loads `yolov8n.pt`, returns list of detections (class, confidence).
  - `violation_logic.py`: Maps detection classes to violation types (e.g. person → "Person Detected").
  - `websocket_manager.py`: Keeps a list of WebSocket connections and broadcasts JSON messages.

---

## Frontend (React + Vite)

- **Stack:** React 19, Vite 7, Tailwind CSS, Lucide icons.
- **Flow:**
  1. `TrafficViolationUI` uses the `useViolationsSocket()` hook.
  2. The hook connects to `ws://127.0.0.1:8000/ws/violations` (or `VITE_WS_VIOLATIONS_URL`).
  3. Each WebSocket message is parsed as JSON and prepended to a `violations` list.
  4. The UI shows stats (total violations, fines) and a list of recent violations (type, vehicle, time, location).
- **Files:**
  - `useViolationsSocket.js`: Single WebSocket connection, state = array of violation objects.
  - `TrafficViolationUI.jsx`: Stats cards + “Recent Violations” list from that array.
  - `App.jsx`: Renders `Header` + `TrafficViolationUI`.

---

## How to run (backend + frontend)

### 1. Backend (terminal 1)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run the app directly:

```bash
cd backend
python -m app.main
```

- First run will download the YOLO model (`yolov8n.pt`) if needed.
- Webcam will start when a client connects to the WebSocket.

### 2. Frontend (terminal 2)

```bash
npm install
npm run dev
```

- Open **http://localhost:5173/**.
- The dashboard will connect to `ws://127.0.0.1:8000/ws/violations` and show violations as the backend detects them.

### 3. Optional: custom WebSocket URL

Copy `.env.example` to `.env` and set:

```env
VITE_WS_VIOLATIONS_URL=ws://127.0.0.1:8000/ws/violations
```

Change the URL if your backend runs on another host/port.

---

---

## Train your own model (user input + Kaggle)

**Training dataset reference:** [https://codeshare.io/final](https://codeshare.io/final) — ye link training datasets ke liye use karein.

You can **train a custom YOLO model** from the dashboard using **Kaggle datasets** for:

- **Helmet detection** – e.g. [abuzarkhaaan/helmetbehncode](https://www.kaggle.com/datasets/abuzarkhaaan/helmetbehncode)
- **Triple ride detection** – e.g. ride-safety or person/vehicle datasets
- **Lane violation detection** – e.g. lane/vehicle datasets

### Setup

1. **Kaggle API**: Create a Kaggle account, then create an API token (Account → Create New Token). Place `kaggle.json` in `~/.kaggle/` (or set `KAGGLE_USERNAME` and `KAGGLE_KEY`).
2. **Backend**: Install deps include `kaggle`: `pip install -r requirements.txt`.

### Flow

1. Open the dashboard and scroll to **“Train your model (Kaggle data)”**.
2. Choose **Task** (Helmet / Triple ride / Lane violation), select a **Kaggle dataset** from the list or enter a slug (e.g. `owner/dataset-name`), set **Epochs**, then click **Start training**.
3. Training runs in the background. Status updates every few seconds (Running → Completed or Failed).
4. When training **completes**, the backend saves the best model to `backend/weights/{task}_best.pt` and updates `model_config.json`. Click **Reload model** (or restart the backend) to use the new model for live detection.
5. Violation logic maps class names from your trained model (e.g. `no_helmet`, `triple_ride`, `lane_violation`) to dashboard labels (No Helmet, Triple Riding, Lane Violation).

### API

- `GET /api/datasets?task=helmet|triple_ride|lane_violation` – suggested Kaggle datasets
- `POST /api/train` – body: `{ "task_type", "kaggle_slug", "epochs" }` – start training
- `GET /api/training/status` – current job status
- `POST /api/model/reload` – reload detector from `model_config.json`

---

## Summary

| Part        | Role |
|------------|------|
| **Backend**  | Webcam → YOLO (default or custom) → violation rules → broadcast JSON over WebSocket on port 8000. Training API: Kaggle download + YOLO train. |
| **Frontend** | WebSocket for live violations; REST for training (datasets, start train, status, reload model). |
| **Connection** | WebSocket URL: `VITE_WS_VIOLATIONS_URL`. API URL: `VITE_API_URL`. |
