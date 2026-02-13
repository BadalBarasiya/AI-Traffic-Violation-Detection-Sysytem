from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame, conf=0.5)
        detections = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                detections.append({
                    "class": cls,
                    "confidence": conf
                })

        return detections

# from ultralytics import YOLO

# class YOLODetector:
#     def __init__(self, model_path="yolov8n.pt"):
#         self.model = YOLO(model_path)

#     def detect(self, frame):
#         results = self.model(frame, conf=0.5)
#         detections = []

#         for r in results:
#             boxes = r.boxes
#             for box in boxes:
#                 cls = int(box.cls[0])
#                 conf = float(box.conf[0])
#                 detections.append({
#                     "class": cls,
#                     "confidence": conf
#                 })

#         return detections
