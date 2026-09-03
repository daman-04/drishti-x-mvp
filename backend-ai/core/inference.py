from ultralytics import YOLO
import cv2
import numpy as np

# Load the YOLO11 model (it will automatically download if not present)
model = YOLO("yolo11n.pt")

def process_frame(frame: np.ndarray, zone_data: dict = None):
    # Run YOLO with ByteTrack tracking
    # We only care about people (0) and vehicles (2: car, 3: motorcycle, 5: bus, 7: truck) for now, maybe animal (15: cat, 16: dog, 17: horse, 18: sheep, 19: cow, 20: elephant, 21: bear, 22: zebra, 23: giraffe)
    results = model.track(frame, persist=True, classes=[0, 2, 3, 5, 7, 15, 16, 17, 18, 19, 20, 21, 22, 23], tracker="bytetrack.yaml", verbose=False)
    
    detections = []
    
    if len(results) > 0 and results[0].boxes is not None:
        boxes = results[0].boxes
        if boxes.id is not None:
            track_ids = boxes.id.int().cpu().tolist()
            cls_ids = boxes.cls.int().cpu().tolist()
            confidences = boxes.conf.cpu().tolist()
            xyxys = boxes.xyxy.cpu().tolist()
            
            for t_id, c_id, conf, xyxy in zip(track_ids, cls_ids, confidences, xyxys):
                # Class name mapping
                class_name = model.names[c_id]
                
                detections.append({
                    "track_id": str(t_id),
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": xyxy, # [x1, y1, x2, y2]
                    "centroid": [ (xyxy[0] + xyxy[2])/2, (xyxy[1] + xyxy[3])/2 ]
                })
                
    return detections
