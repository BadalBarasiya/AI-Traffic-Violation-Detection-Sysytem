# COCO class IDs (yolov8n default)
COCO_PERSON = 0
COCO_MOTORCYCLE = 3

# Class names that indicate helmet IS detected (custom models)
HELMET_CLASSES = {"helmet", "with_helmet", "helmet_on"}
# Class names that indicate NO helmet (custom models)
NO_HELMET_CLASSES = {"no_helmet", "without_helmet", "helmetless"}

# Default COCO class id -> violation type (when using pretrained yolov8n)
COCO_VIOLATION_MAP = {
    0: "Person Detected",   # person
    3: "Motorcycle",        # motorcycle - can combine with no_helmet/triple later
}
# Custom model: class name (lower) -> violation type
CLASS_NAME_VIOLATION_MAP = {
    "no_helmet": "No Helmet",
    "without_helmet": "No Helmet",
    "helmetless": "No Helmet",
    "triple_ride": "Triple Riding",
    "triple_rider": "Triple Riding",
    "triple_riding": "Triple Riding",
    "lane_violation": "Lane Violation",
    "wrong_lane": "Lane Violation",
}


def check_violations(detections, class_names=None):
    """
    Check detections and return list of violations.
    If class_names is provided (from custom model), map by class name.
    Otherwise use COCO class ids for default model.
    """
    violations = []
    seen_types = set()

    for d in detections:
        cls_id = d.get("class")
        class_name = (d.get("class_name") or "").strip().lower().replace(" ", "_")
        if not class_name and class_names:
            class_name = (class_names[cls_id] if isinstance(class_names, (list, tuple)) else class_names.get(cls_id, "")).lower().replace(" ", "_")

        # Custom model: map by class name
        if class_name:
            for key, vtype in CLASS_NAME_VIOLATION_MAP.items():
                if key in class_name and vtype not in seen_types:
                    violations.append({"type": vtype})
                    seen_types.add(vtype)

        # Default COCO fallback
        if not class_name and cls_id in COCO_VIOLATION_MAP:
            vtype = COCO_VIOLATION_MAP[cls_id]
            if vtype not in seen_types:
                violations.append({"type": vtype})
                seen_types.add(vtype)

    return violations


def check_image_upload_violations(detections) -> tuple[str, float]:
    """
    Check detections for manual image upload. Returns (violation_type, confidence).
    violation_type: "Helmet Violation" | "Triple Riding" | "None"
    """
    if not detections:
        return ("None", 0.0)

    persons = [d for d in detections if d.get("class") == COCO_PERSON or
               (d.get("class_name") or "").lower() in ("person", "rider")]
    motorcycles = [d for d in detections if d.get("class") == COCO_MOTORCYCLE or
                   (d.get("class_name") or "").lower() in ("motorcycle", "bike", "motorbike")]
    class_names = {(d.get("class_name") or "").strip().lower().replace(" ", "_") for d in detections}

    has_helmet = bool(class_names & HELMET_CLASSES)
    has_no_helmet = bool(class_names & NO_HELMET_CLASSES)

    # Triple Riding: motorcycle + >= 3 persons
    if motorcycles and len(persons) >= 3:
        conf = max((d.get("confidence", 0) for d in persons + motorcycles), default=0.5)
        return ("Triple Riding", round(conf, 2))

    # Helmet Violation: rider (person) on motorcycle, no helmet detected
    if motorcycles and persons:
        if has_no_helmet:
            conf = max((d.get("confidence", 0) for d in persons + motorcycles), default=0.5)
            return ("Helmet Violation", round(conf, 2))
        if not has_helmet:
            # COCO/default model: no helmet class; motorcycle + person = assume violation
            conf = max((d.get("confidence", 0) for d in persons + motorcycles), default=0.5)
            return ("Helmet Violation", round(conf, 2))

    return ("None", 0.0)


# import random

# def check_violations(detections):
#     violations = []

#     classes = [d.get("class") for d in detections]

#     PERSON = 0
#     MOTORCYCLE = 3
#     CAR = 2

#     # Triple Riding (3 persons + motorcycle)
#     if classes.count(PERSON) >= 3 and MOTORCYCLE in classes:
#         violations.append({"type": "Triple Riding"})

#     # No Helmet (simulated)
#     if MOTORCYCLE in classes and PERSON in classes:
#         violations.append({"type": "No Helmet"})

#     # Wrong Way (random simulation)
#     if CAR in classes and random.random() > 0.95:
#         violations.append({"type": "Wrong Way Driving"})

#     return violations


# def check_violations(detections):
#     violations = []

#     classes = [d["class"] for d in detections]

#     # COCO IDs:
#     PERSON = 0
#     BICYCLE = 1
#     CAR = 2
#     MOTORCYCLE = 3
#     TRAFFIC_LIGHT = 9

#     # 🚦 Example 1: Motorcycle detected (test rule)
#     if MOTORCYCLE in classes:
#         violations.append({
#             "type": "Motorcycle Detected"
#         })

#     # 🚗 Example 2: Car detected
#     if CAR in classes:
#         violations.append({
#             "type": "Car Detected"
#         })

#     return violations












# # ---------------------***************
# # import random

# # def check_violations(detections):
# #     violations = []

# #     # Temporary random trigger so you can test frontend
# #     if random.random() > 0.5:
# #         violations.append({
# #             "type": "No Helmet"
# #         })

# #     return violations



# # ------------------------***--------------------
# # def check_violations(detections):
# #     violations = []

# #     classes = [d["class"] for d in detections]

# #     # Example rule: Bike + Person but no Helmet
# #     if 1 in classes and 2 in classes and 3 not in classes:
# #         violations.append({
# #             "type": "No Helmet",
# #             "fine": 1000
# #         })

# #     return violations
