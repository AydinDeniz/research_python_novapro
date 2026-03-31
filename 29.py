import cv2
import dronekit
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import numpy as np

# Connect to the drone
vehicle = connect('udp:127.0.0.1:14551', wait_ready=True)

# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Function to detect obstacles
def detect_obstacles(frame):
    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    return boxes, confidences, class_ids, indexes

# Function to adjust flight path
def adjust_flight_path(boxes, frame):
    height, width, _ = frame.shape
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            center_x = x + w // 2
            center_y = y + h // 2
            if center_x < width // 2:
                vehicle.send_ned_velocity(0, 0.5, 0)  # Move right
            elif center_x > width // 2:
                vehicle.send_ned_velocity(0, -0.5, 0)  # Move left
            if center_y < height // 2:
                vehicle.send_ned_velocity(0.5, 0, 0)  # Move up
            elif center_y > height // 2:
                vehicle.send_ned_velocity(-0.5, 0, 0)  # Move down

# Main loop
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    boxes, confidences, class_ids, indexes = detect_obstacles(frame)
    adjust_flight_path(boxes, frame)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
vehicle.close()