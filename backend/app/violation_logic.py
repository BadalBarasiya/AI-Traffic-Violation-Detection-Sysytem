
def check_violations(detections):
    violations = []

    classes = [d.get("class") for d in detections]

    PERSON = 0

    if PERSON in classes:
        violations.append({
            "type": "Person Detected"
        })

    return violations
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
