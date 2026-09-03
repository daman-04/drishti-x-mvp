from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
import threading
from core.stream_manager import StreamManager
from core.database import SessionLocal, Event, Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize stream manager with sample video
stream_mgr = StreamManager(camera_id="cam_01", source="sample.mp4")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting stream manager...")
    if stream_mgr.start():
        task = asyncio.create_task(stream_mgr.process_loop())
    else:
        logger.error("Could not start video source")
    yield
    logger.info("Shutting down stream manager...")
    stream_mgr.stop()

app = FastAPI(title="DRISHTI-X MVP API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We poll the queue for frames and send them to the client
            payload = await stream_mgr.frame_queue.get()
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            evt = await stream_mgr.alert_queue.get()
            
            # Save to DB (async to sync wrap for simple MVP)
            db = SessionLocal()
            try:
                db_event = Event(
                    camera_id=evt['camera_id'],
                    track_id=str(evt['track_id']),
                    class_name=evt['class_name'],
                    threat_score=evt['threat_score'],
                    event_type=evt['event_type'],
                    explanation=evt['explanation']
                )
                db.add(db_event)
                db.commit()
            except Exception as e:
                logger.error(f"DB Error: {e}")
            finally:
                db.close()
                
            await websocket.send_json(evt)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/v1/cameras")
def get_cameras():
    return [{"id": "cam_01", "name": "Main Gate", "status": "active" if stream_mgr.running else "inactive"}]

@app.get("/api/v1/events")
def get_events():
    db = SessionLocal()
    events = db.query(Event).order_by(Event.created_at.desc()).limit(20).all()
    db.close()
    return [{"id": e.id, "camera_id": e.camera_id, "track_id": e.track_id, "class_name": e.class_name, "threat_score": e.threat_score, "event_type": e.event_type, "explanation": e.explanation, "created_at": e.created_at} for e in events]
