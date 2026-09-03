# DRISHTI-X: Product Requirements Document
**Version:** 1.0 (MVP) | **Status:** Approved for Implementation | **Target:** SIH26187 (Ministry of Home Affairs)

---

## 1. Executive Summary
DRISHTI-X is an AI-powered Video Analytics ecosystem designed for the Ministry of Home Affairs to retrofit existing border CCTV infrastructure with predictive intelligence. Moving beyond rudimentary object detection, DRISHTI-X acts as an autonomous threat-reasoning engine. It ingests standard RTSP feeds, processes them via an optimized YOLOv11/ByteTrack pipeline on edge/GPU nodes, and delivers context-aware, explainable alerts. The goal for the 1-hour MVP implementation is to establish the complete data pipeline: RTSP ingestion -> Inference -> Threat Scoring -> API -> Real-time UI.

## 2. Vision Statement
To transform passive border surveillance networks into predictive, intelligent ecosystems that tell operators *what will happen next*, rather than *what just happened*.

## 3. Problem Statement
Current MHA border CCTV infrastructure is passive. It requires constant human monitoring, leading to fatigue and missed incursions. Existing analytics (if any) are limited to basic motion detection or single-frame object detection, resulting in massive false-positive fatigue (e.g., animals triggering alarms) and no contextual understanding of behavior across time or multiple cameras.

## 4. Current System Limitations
*   **Passive Hardware:** Cameras only record; they do not analyze.
*   **Siloed Vision:** A target moving across three cameras is treated as three separate events.
*   **Reactive vs. Predictive:** Alarms trigger *after* a perimeter breach, not during the approach.
*   **Black-Box Alarms:** Motion sensors do not explain *why* an alarm was triggered.
*   **High False Positive Rate (FPR):** Shadows, wildlife, and weather cause alert fatigue.

## 5. Product Goals
1.  **Zero-Hardware Replacement:** 100% compatibility with existing IP/RTSP cameras.
2.  **Predictive Reasoning:** Shift from "fence crossed" to "fence crossing probability: 85%".
3.  **Explainability (XAI):** Every alert includes a semantic reason (e.g., "Night movement + Suspicious Route + No Face").
4.  **Operator Efficiency:** Reduce false positives by >90% via context-aware threat scoring.

## 6. Success Metrics (MVP)
| Metric | MVP Target | Measurement Method |
| :--- | :--- | :--- |
| **Pipeline Latency** | < 250 ms | Frame capture to DB insert |
| **Detection Recall** | > 95% | On standard human/vehicle datasets |
| **False Positive Rate** | < 5% | Measured against baseline motion detection |
| **Threat Score Accuracy** | > 90% | Human-in-the-loop validation |
| **Uptime** | 99.9% | Container orchestration metrics |

## 7. Target Users
*   **Control Room Operator:** Monitors live feeds, validates alerts, dispatches units. Needs low-latency UI and clear alerts.
*   **Border Security Officer (Field):** Receives actionable intelligence (snapshot, location, threat level).
*   **Senior Command Officer:** Reviews daily incident timelines, heatmaps, and post-event analytics.
*   **System Administrator:** Manages RTSP streams, server health, and virtual fence coordinates.

## 8. User Personas
*   **Operator Om:** 45 years old. Fatigued by staring at 16 grids. Needs the UI to aggressively highlight *only* what matters and dim the rest.
*   **Commander Kapoor:** 50 years old. Doesn't want to watch video. Wants the "story" of an incident in a 4-step timeline.

## 9. User Stories (MVP Scope: 25 Stories)
**Monitoring & Feeds**
1. *As an Operator*, I want to view a 2x2 or 4x4 grid of live RTSP feeds so I can monitor key sectors.
2. *As an Operator*, I want bounding boxes rendered on live feeds only for entities with a Threat Score > 50, to reduce visual clutter.
3. *As an Operator*, I want to see a "Predicted Path" vector arrow on moving targets.
4. *As an Operator*, I want to manually toggle X-Ray mode (show all detections vs. threat only).
5. *As an Operator*, I want to click a camera to view it in full screen with deep metadata overlays.

**Alerts & Triage**
6. *As an Operator*, I want a real-time sidebar of incoming alerts sorted by Threat Score.
7. *As an Operator*, I want an audible chime for Critical (Score > 85) alerts.
8. *As an Operator*, I want to click an alert to instantly play the 5-second video clip of the incident.
9. *As an Operator*, I want to read a plain-English explanation for every alert (e.g., "Person running toward fence at 2 AM").
10. *As an Operator*, I want to mark an alert as "True Positive" or "False Positive" to reinforce the system.

**Analytics & Timelines**
11. *As a Commander*, I want to view a chronological "Incident Story" merging data from 3 cameras into 1 timeline.
12. *As a Commander*, I want a dashboard showing threat frequency by hour and sector.
13. *As a Commander*, I want to see a heat map of loitering zones to optimize patrol routes.
14. *As a Commander*, I want to export an incident report containing keyframes and metadata as a PDF.
15. *As a Commander*, I want to search past events by entity type (e.g., "Red Vehicle" or "Person + Backpack").

**System & Configuration**
16. *As an Admin*, I want to add a new camera by entering its RTSP URL and credentials.
17. *As an Admin*, I want to draw polygon "Restricted Zones" directly on a camera's static frame.
18. *As an Admin*, I want to draw polyline "Virtual Fences" and define the "illegal crossing direction".
19. *As an Admin*, I want to configure baseline normal behavior for a camera (e.g., "Vehicles allowed, pedestrians not").
20. *As an Admin*, I want to monitor GPU memory and container health from the settings page.

**Tracking & Identity**
21. *As a System*, I need to maintain a persistent ID for an object as long as it remains in frame.
22. *As a System*, I need to attempt Re-ID if an object leaves Camera 1 and enters Camera 2 within 60 seconds.
23. *As a System*, I need to extract and log license plates to the database when a vehicle is detected.
24. *As a System*, I need to extract face crops if a person is close enough to the camera.
25. *As a System*, I need to classify the carrying of objects (e.g., weapons/backpacks) if visible.

## 10. Functional Requirements
| Module | Requirement | Details |
| :--- | :--- | :--- |
| **Ingestion** | Multi-stream processing | Handle >= 4 1080p RTSP feeds concurrently per GPU. |
| **Inference** | Object Detection | YOLOv11 recognizing Person, Vehicle, Animal. |
| **Tracking** | ByteTrack integration | Maintain consistent track IDs per stream. |
| **Geofencing** | Virtual perimeters | Polygon Point-in-Polygon (Ray Casting algorithm) checking. |
| **State Eng.** | Temporal memory | Track history over N frames to compute velocity/loitering. |
| **Alerting** | Pub/Sub via Redis | Push normalized JSON payloads to frontend via WebSockets. |

## 11. Non-Functional Requirements
*   **Performance:** Inference pipeline must run at >= 25 FPS on an NVIDIA RTX 3060/4060 or T4 equivalent.
*   **Latency:** Glass-to-glass latency (camera to UI) must not exceed 2 seconds.
*   **Reliability:** Auto-restart RTSP stream ingestion if connection drops (exponential backoff).
*   **Scalability:** Microservices architecture; AI workers can scale horizontally via Docker Swarm/K8s.
*   **Security:** JWT-based API authentication. No raw video stored permanently (only 10s alert clips).

## 12. System Architecture
```text
+-------------------+      +-------------------------------------------------+
|  CCTV Network     |      |                 AI INFERENCE NODE               |
|  (RTSP Streams)   |      |                                                 |
|   Cam 1 .. Cam N  | ===> | [FFmpeg Decoder] -> [Frame Buffer (Shared Mem)] |
+-------------------+      |                           |                     |
                           |                           v                     |
                           |  [YOLOv11 TensorRT] -> [ByteTrack / BoT-SORT]   |
                           +---------------------------|---------------------+
                                                       |
+------------------------------------------------------v---------------------+
|                     CONTEXT & REASONING ENGINE (Python)                    |
|  +----------------+   +-------------------+   +-------------------------+  |
|  | State Tracker  |   | Behaviour Module  |   | Threat Scoring Alg      |  |
|  | (Velocities)   |   | (Loiter/Fence)    |   | (Context + Prediction)  |  |
|  +----------------+   +-------------------+   +-------------------------+  |
+------------------------------------------------------|---------------------+
                                                       | (JSON Meta & Clips)
+-------------------+      +---------------------------v---------------------+
|  FRONTEND APP     |      |                  BACKEND API                    |
|  (Next.js / UI)   | <=== | [FastAPI Router]  <--->  [PostgreSQL (Schema)]  |
|  WebSockets (SSE) |      |        ^                                        |
+-------------------+      |        |---- [Redis Pub/Sub (Live Events)]      |
                           +-------------------------------------------------+
```

## 13. AI Pipeline Detailed
1.  **Decoder:** OpenCV `VideoCapture` is too slow for multi-camera. Use `PyAV` or `GStreamer` to decode RTSP directly to GPU memory.
2.  **Detection:** YOLOv11 (FP16 quantized) detects bounding boxes (x1, y1, x2, y2), class, and confidence.
3.  **Tracking:** ByteTrack uses Kalman Filters and Hungarian algorithm to link bounding boxes across frames without heavy Re-ID models, achieving 600+ FPS tracking.
4.  **Feature Extraction (Conditional):** If `class == vehicle` and area > threshold, pass crop to PaddleOCR.
5.  **State Aggregation:** The pipeline maintains a `TrackState` dictionary. For every frame, it updates the centroid (xc, yc) history.
6.  **Reasoning Trigger:** The updated `TrackState` is fed into the Threat & Predictive Engine to evaluate rule breaches.

## 14. Feature Specifications
| Feature | Inputs | Business Logic | Outputs |
| :--- | :--- | :--- | :--- |
| **Virtual Fence** | BBox coordinates, Polyline coords | Line intersection algorithm between Track's movement vector (last 5 frames) and Fence polyline. | Boolean `crossed`, Direction of crossing. |
| **Loitering** | Centroid history over time T | If Delta distance of centroid < threshold for time t > limit. | Boolean `is_loitering`, duration. |
| **Night Vision Analytics** | Frame timestamp | If time > 18:00, increase sensitivity weights for person detection. | Adjusted threat scores. |

## 15. Threat Scoring Algorithm
DRISHTI-X uses a weighted multi-variate polynomial to assign a score S_total in [0, 100].

`S_total = min(100, Sum(W_i * C_i * P_factor))`

**Variables:**
*   `W_i`: Base weight of the event type.
*   `C_i`: Contextual multiplier (Time, Location).
*   `P_factor`: Predictive urgency (How soon will the breach happen?).

**Weight Table (W_i):**
| Event | Base Weight | Multipliers (C_i) |
| :--- | :--- | :--- |
| Person in Restricted Zone | 70 | x1.5 (Night), x1.2 (Multiple people) |
| Vehicle Stopped near Fence | 60 | x1.3 (No License Plate) |
| Loitering > 5 mins | 40 | x1.2 (Night) |
| Predictive Intrusion (>80%) | 85 | x1.0 |
| Animal detected | 5 | x0.1 (Auto-suppress) |

*Example Calculation:* Person detected in Restricted Zone (70) at Night (x1.5). Score = 105 -> Capped at 100. Classification: **CRITICAL**.

## 16. Predictive Intrusion Algorithm
Instead of waiting for a line-crossing event, we predict it.
1.  **Calculate Velocity Vector (v):** Use the centroid position at t_0 and t_{-15} (15 frames ago).
2.  **Trajectory Projection:** Extend the ray r from current centroid along v.
3.  **Intersection Check:** Find intersection point I between r and virtual fence line segment F.
4.  **Time to Impact (TTI):** TTI = (Distance to I) / |v|.
5.  **Probability (P):**
    *   If r does not intersect F: P = 0
    *   If intersects: P = 100 * e^(-k * TTI) (where k is a tuning constant, e.g., 0.5).
6.  **Action:** If P > 80%, fire `PREDICTIVE_INTRUSION_ALERT`.

## 17. Behaviour Analytics Module
*   **Running:** Calculate instantaneous velocity in pixels/sec. If velocity > threshold (calibrated per camera perspective), flag as `Running`.
*   **Wrong Direction:** Define an allowed direction vector a. If track vector v has a negative dot product with a (v * a < 0), flag `WrongDirection`.
*   **Unusual Gathering:** Perform DBSCAN clustering on person centroids. If cluster size >= 4 in a non-gathering zone, flag `Gathering`.
*   **Fence Following:** If trajectory vector is parallel to fence vector within a distance threshold D for t > 10s.

## 18. Cross Camera Tracking Strategy (Re-ID Lite)
For the MVP, implementing a massive Vision Transformer (ViT) for Re-ID is too slow. We use **Spatio-Temporal Topology**:
1.  Map camera FOVs on a 2D global plane (Camera 1 exits North, Camera 2 enters South).
2.  When Track ID #12 leaves Cam 1 North, create a `GhostTrack` with expected arrival window at Cam 2 South.
3.  If a new track appears in Cam 2 South within the time window Delta t, assign it the semantic identity of Track ID #12.
4.  *Fallback:* Extract color histograms (HSV) of the bounding box to match the `GhostTrack` signature.

## 19. Database Design (PostgreSQL)
```sql
-- Core schemas for rapid deployment
CREATE TABLE cameras (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    rtsp_url TEXT,
    zone_data JSONB, -- Stores polygons & lines
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE events (
    id UUID PRIMARY KEY,
    camera_id UUID REFERENCES cameras(id),
    track_id VARCHAR(50),
    class_name VARCHAR(50),
    threat_score INT,
    event_type VARCHAR(50), -- 'loitering', 'intrusion'
    explanation TEXT,
    snapshot_path TEXT,
    video_clip_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast time-series queries
CREATE INDEX idx_events_created_at ON events(created_at DESC);
CREATE INDEX idx_events_threat ON events(threat_score DESC);
```

## 20. REST API Design (FastAPI)
| Method | Endpoint | Purpose | Request Body | Response (200 OK) |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/cameras` | Add new camera | `{"name":"Cam1", "url":"rtsp://..."}` | `{"id": "uuid", "status":"connected"}` |
| `GET` | `/api/v1/cameras` | List cameras | - | `[{"id":"uuid", "name":"Cam1"}]` |
| `GET` | `/api/v1/events` | Get alerts | `?min_score=50&limit=20` | `[{"event_type": "intrusion", "score":95}]` |
| `POST` | `/api/v1/config/zone`| Set Geofence | `{"cam_id":"..", "polygon":[[x,y]..]}`| `{"status": "updated"}` |
| `GET` | `/ws/alerts` | Live Events | (WebSocket / SSE connection) | Stream of JSON event objects. |

## 21. Frontend Design (Next.js)
*   **Tech:** React, TailwindCSS, Zustand (State), Socket.io-client.
*   **Layout:**
    *   **Left Sidebar (15%):** Navigation (Dashboard, Cameras, Analytics, Settings).
    *   **Main Stage (60%):** 2x2 Camera Grid using WebRTC or HTTP-FLV for ultra-low latency playback. Overlays rendered via SVG layered on top of video elements.
    *   **Right Sidebar (25%):** Live Alert Feed. Cards with red/yellow/green borders based on Threat Score. Auto-scrolls.
*   **Incident Center:** A timeline view showing connected events chronologically.

## 22. UI Wireframes (ASCII)
```text
+-----------------------------------------------------------------------------+
| [DRISHTI-X]  Dashboard | Cameras | Analytics | Settings       [Admin User]  |
+-----------------------------------------------------------------------------+
| +---------------------------------------+ +-------------------------------+ |
| | LIVE FEEDS (X-Ray Mode: ON)           | | THREAT INTELLIGENCE FEED      | |
| | +-----------------+ +---------------+ | |                               | |
| | | CAM 1: SEC A    | | CAM 2: SEC B  | | | [CRITICAL] 95/100  - 10:42  | |
| | | [ ] Person 98%  | |               | | | Predictive Intrusion        | |
| | | -> TTI: 4s      | |               | | | Cam 1 - 85% probability     | |
| | |  \              | |               | | | [ VIEW CLIP ] [ DISMISS ]   | |
| | | ---\-- Fence    | |               | | +-------------------------------+ |
| | +-----------------+ +---------------+ | |                               | |
| | +-----------------+ +---------------+ | | | [WARNING] 65/100   - 10:40  | |
| | | CAM 3: SEC C    | | CAM 4: SEC D  | | | Vehicle stopped             | |
| | |   Loitering     | |               | | | Cam 3 - No Plate Detected   | |
| | +-----------------+ +---------------+ | | +-------------------------------+ |
| +---------------------------------------+ +-------------------------------+ |
+-----------------------------------------------------------------------------+
```

## 23. Folder Structure (MVP Implementable in 1 Hour)
```bash
drishti-x-mvp/
├── backend-ai/                  # FastAPI + YOLO engine
│   ├── main.py                  # API routes & WS endpoints
│   ├── core/
│   │   ├── stream_manager.py    # Threaded RTSP reader
│   │   ├── inference.py         # YOLOv11 + ByteTrack runner
│   │   ├── reasoning.py         # Threat Score & Predictive math
│   │   └── database.py          # Postgres connections
│   ├── models/                  # Downloaded .pt / .onnx weights
│   └── requirements.txt         
├── frontend/                    # Next.js UI
│   ├── package.json
│   ├── src/
│   │   ├── app/                 # Next.js App Router (page.tsx)
│   │   ├── components/
│   │   │   ├── CameraGrid.tsx   # Canvas/Video components
│   │   │   ├── AlertFeed.tsx    # Live WebSocket consumer
│   │   │   └── BBoxOverlay.tsx  # Renders SVG boxes
│   │   └── store/               # Zustand state
└── docker-compose.yml           # Boots Postgres, Redis, API, UI
```

## 24. Development Roadmap (1-Hour Rapid Prototype Sprint)
*   **Minute 00-10:** Environment Setup. Initialize Next.js and FastAPI environments; setup SQLite in-memory DB as placeholder.
*   **Minute 10-25:** Ingestion & Inference. Build `stream_manager.py` and `inference.py` using a pre-trained YOLOv11 model for basic RTSP/Webcam frame processing.
*   **Minute 25-40:** Reasoning & Logic. Implement `reasoning.py` for Geofence intersection logic and calculating base Threat Scores.
*   **Minute 40-50:** API & WebSockets. Expose FastAPI endpoints and basic WebSocket broadcasting for live alerts.
*   **Minute 50-60:** Frontend Dashboard. Launch Next.js Camera Grid with SVG overlays and Alert Sidebar integration to catch the WebSocket events.

## 25. Testing Strategy
*   **AI Evaluation:** Run inference on the MOT17/MOT20 datasets to verify tracking continuity.
*   **Unit Testing:** `pytest` for `reasoning.py` (feed dummy vectors to ensure TTI and Threat Scores calculate exactly as expected).
*   **Load Testing:** Attach 8 simultaneous 1080p RTSP feeds to the GPU and measure memory leak/VRAM usage over 2 hours.
*   **Failover Testing:** Unplug the IP camera. Verify the stream manager attempts reconnection without crashing the main loop.

## 26. Deployment Strategy
*   **Hardware:** Deploy locally on edge hardware (NVIDIA Jetson AGX Orin) or local Command Center server (RTX 4090). Cloud deployment is strictly avoided for video streams due to bandwidth costs and security policies.
*   **Containerization:** `docker-compose` wrapping the API (with `--gpus all` flag) and UI.
*   **Video Serving:** Backend acts as an RTSP proxy. Avoid trans-coding in the backend to save CPU; pass H.264 streams directly to frontend via Media Source Extensions (MSE) or WebRTC.

## 27. Future Scope
*   **Drone Fusion:** Ingesting RTSP feeds from patrol drones dynamically.
*   **Thermal Camera Integration:** Custom weights for FLIR camera feeds to detect body heat in zero-lux environments.
*   **LLM Incident Reports:** Feeding the structured JSON "Incident Timeline" into an LLM to auto-generate official text reports for command officers.
*   **Audio Analytics:** Detecting gunshots or breaking glass via integrated camera microphones.

## 28. Risk Analysis
| Risk Type | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Technical** | High latency due to decoding bottlenecks. | Use hardware-accelerated FFmpeg (NVDEC). Process at 10-15 FPS instead of 30 FPS. |
| **Operational** | Cameras moved by wind altering geofences. | Implement dynamic frame registration (homography) to realign zones automatically. |
| **Environmental** | Heavy fog/rain rendering YOLO blind. | Utilize image dehazing pre-processing algorithms and train on low-visibility datasets. |

## 29. Competitive Comparison
| Feature | Legacy VMS (e.g., Milestone, Hikvision) | Generic AI Wrappers | **DRISHTI-X** |
| :--- | :--- | :--- | :--- |
| **Detection focus** | Pixels (Motion) | Objects (Person/Car) | **Behaviors & Intent** |
| **Alert Trigger** | Line Crossed | Object Detected | **Predictive (Will Cross)** |
| **Alert Context** | "Motion Alarm" | "Person Detected" | **"Person running toward fence at night (Threat: 92)"** |
| **Infrastructure** | Proprietary Cameras | High-bandwidth Cloud | **Hardware Agnostic, Edge GPU** |

## 30. Appendix
*   **Assumptions:** Cameras are fixed (PTZ cameras require dynamic coordinate mapping not included in MVP). Cameras have at least 1080p resolution.
*   **Glossary:**
    *   *RTSP:* Real-Time Streaming Protocol.
    *   *BBox:* Bounding Box.
    *   *TTI:* Time to Impact.
    *   *Re-ID:* Re-Identification.
*   **References:** YOLOv11 Documentation, ByteTrack Paper, Smart India Hackathon Problem Statement #SIH26187.
