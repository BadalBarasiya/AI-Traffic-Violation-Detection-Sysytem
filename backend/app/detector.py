from ultralytics import YOLO


class YOLODetector:
    def __init__(self, model_path="yolov8n.pt", class_names=None):
        self.model_path = model_path
        self.class_names = class_names
        self.model = YOLO(model_path)

    def reload(self, model_path=None, class_names=None):
        """Reload model (e.g. after training)."""
        from app.model_config import get_model_path, get_class_names
        path = model_path or get_model_path()
        names = class_names if class_names is not None else get_class_names()
        self.model = YOLO(path)
        self.model_path = path
        self.class_names = names or (list(self.model.names.values()) if hasattr(self.model, "names") else None)

    def detect(self, frame, imgsz=640, verbose=False, max_det=30):
        results = self.model(frame, conf=0.45, imgsz=imgsz, verbose=verbose, max_det=max_det)
        detections = []
        names = self.class_names or (getattr(self.model, "names", None) or {})

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = names[cls] if isinstance(names, (list, tuple)) else names.get(cls, str(cls))
                detections.append({
                    "class": cls,
                    "class_name": class_name,
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
