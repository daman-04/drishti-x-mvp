import cv2
import asyncio
import time
import base64
from core.inference import process_frame
from core.reasoning import analyze_track
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamManager:
    def __init__(self, camera_id, source):
        self.camera_id = camera_id
        self.source = source
        self.cap = None
        self.running = False
        self.zone_data = {
            # Dummy restricted zone right in the middle
            'polygons': [[(300, 200), (600, 200), (600, 500), (300, 500)]],
            # Dummy line
            'lines': [[(100, 100), (700, 700)]]
        }
        self.alert_queue = None
        self.frame_queue = None
    
    def start(self):
        self.alert_queue = asyncio.Queue()
        self.frame_queue = asyncio.Queue(maxsize=30)
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            logger.error(f"Failed to open source {self.source}")
            return False
        self.running = True
        return True
        
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            
    async def process_loop(self):
        logger.info("Process loop started")
        try:
            while self.running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    logger.info("Video stream ended, looping...")
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.source)
                    # Small sleep to prevent instant 100% CPU spin if source is totally broken
                    await asyncio.sleep(0.1) 
                    continue
                    
                # Resize for speed
                frame = cv2.resize(frame, (640, 480))
                
                # Process via YOLO + ByteTrack
                detections = process_frame(frame, self.zone_data)
                current_time = time.time()
                
                # Analyze and score
                events_to_emit = []
                for det in detections:
                    score, event_type, explanation = analyze_track(
                        det['track_id'], 
                        det['class_name'], 
                        det['centroid'], 
                        det['bbox'], 
                        self.zone_data, 
                        current_time
                    )
                    
                    det['threat_score'] = score
                    det['event_type'] = event_type
                    
                    if score > 50:
                        events_to_emit.append({
                            "camera_id": self.camera_id,
                            "track_id": det['track_id'],
                            "class_name": det['class_name'],
                            "threat_score": score,
                            "event_type": event_type,
                            "explanation": explanation,
                            "timestamp": current_time,
                            "bbox": det['bbox']
                        })
                        
                # Encode frame to jpeg for streaming
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                b64_frame = base64.b64encode(buffer).decode('utf-8')
                
                payload = {
                    "camera_id": self.camera_id,
                    "frame": b64_frame,
                    "detections": detections
                }
                
                # Put in queue (drop old frames if full)
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                await self.frame_queue.put(payload)
                
                # Put alerts
                for evt in events_to_emit:
                    await self.alert_queue.put(evt)
                    
                # Simulate real-time (~25 FPS) if playing from a file
                await asyncio.sleep(0.04)
        except Exception as e:
            logger.error(f"Error in process_loop: {e}", exc_info=True)
            self.stop()
