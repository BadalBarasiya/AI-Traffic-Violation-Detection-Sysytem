from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import asyncio
import random
from datetime import datetime

from app.detector import YOLODetector
from app.violation_logic import check_violations
from app.websocket_manager import ConnectionManager

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

# Load YOLO model once at startup
detector = YOLODetector("yolov8n.pt")


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

                locations = ["SG Highway", "CG Road", "Ashram Road", "Ring Road", "Satellite", "Paldi"]
                vehicle_prefixes = ["GJ-01-AB", "GJ-05-CD", "GJ-27-EF", "GJ-18-GH"]

                fines = {
                    "Triple Riding": 2000,
                    "No Helmet": 1000,
                    "Wrong Way Driving": 3000,
                    "Person Detected": 500
                }

                violation_type = v.get("type", "Unknown")

                violation_data = {
                    "id": f"V{random.randint(1000,9999)}",
                    "type": violation_type,
                    "vehicle": f"{random.choice(vehicle_prefixes)}-{random.randint(1000,9999)}",
                    "speed": "-",
                    "time": datetime.now().strftime("%I:%M %p"),
                    "location": random.choice(locations),
                    "fine": fines.get(violation_type, 500),
                    "status": "Pending"
                }

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