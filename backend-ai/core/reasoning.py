import math
import time

# Dictionary to hold history of track centroids
# Format: { track_id: { 'history': [(timestamp, centroid_x, centroid_y), ...], 'class_name': str, 'last_score': int, 'last_event': str } }
track_states = {}

def point_in_polygon(point, polygon):
    """Ray casting algorithm to check if point is in polygon."""
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xints:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def check_intersection(p1, p2, p3, p4):
    """Check if line segment p1-p2 intersects with p3-p4."""
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def analyze_track(track_id, class_name, centroid, bbox, zone_data, current_time):
    global track_states
    
    if track_id not in track_states:
        track_states[track_id] = {
            'history': [], 
            'class_name': class_name, 
            'last_score': 0, 
            'last_event': 'Normal',
            'last_alert_time': 0
        }
    
    state = track_states[track_id]
    state['history'].append((current_time, centroid[0], centroid[1]))
    
    # Keep only last 10 seconds of history
    if len(state['history']) > 300:
        state['history'] = state['history'][-300:]
        
    # Check cooldown (throttle alerts to max 1 per 2 seconds per track)
    if current_time - state.get('last_alert_time', 0) < 2.0:
        return 0, "Cooldown", "Alert throttled"
        
    score = 0
    event_type = "Normal"
    explanation = "Normal movement detected."
    
    # Example logic based on PRD
    
    # 1. Animal auto-suppression
    animal_classes = ['cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
    if class_name in animal_classes:
        score = 5
        event_type = "Animal Detected"
        explanation = f"Animal ({class_name}) detected. Suppressed alert."
        state['last_score'] = score
        state['last_event'] = event_type
        return score, event_type, explanation
        
    # Default Base Weights
    if class_name == 'person':
        base_weight = 70
    elif class_name in ['car', 'motorcycle', 'bus', 'truck']:
        base_weight = 60
    else:
        base_weight = 10
        
    multiplier = 1.0
    
    # Check night time (simple stub, e.g., current local time hour > 18 or < 6)
    hour = time.localtime(current_time).tm_hour
    if hour >= 18 or hour < 6:
        multiplier *= 1.5
    
    # 2. Zone Intrusion Check
    is_in_restricted_zone = False
    if zone_data and 'polygons' in zone_data:
        for poly in zone_data['polygons']:
            if point_in_polygon(centroid, poly):
                is_in_restricted_zone = True
                break
                
    if is_in_restricted_zone:
        score = base_weight * multiplier
        event_type = "Intrusion"
        explanation = f"{class_name.capitalize()} detected in Restricted Zone."
        if score > 100: score = 100
        state['last_score'] = score
        state['last_event'] = event_type
        if score > 50: state['last_alert_time'] = current_time
        return int(score), event_type, explanation

    # 3. Virtual Fence Crossing Check
    # Need at least 2 points
    if len(state['history']) >= 2 and zone_data and 'lines' in zone_data:
        p1 = (state['history'][-2][1], state['history'][-2][2])
        p2 = (centroid[0], centroid[1])
        for line in zone_data['lines']: # line format: [(x1,y1), (x2,y2)]
            if check_intersection(p1, p2, line[0], line[1]):
                score = 85 * multiplier
                event_type = "Fence Crossed"
                explanation = f"{class_name.capitalize()} crossed virtual fence."
                if score > 100: score = 100
                state['last_score'] = score
                state['last_event'] = event_type
                if score > 50: state['last_alert_time'] = current_time
                return int(score), event_type, explanation
                
    # 4. Predictive Intrusion (Simplified TTI)
    if len(state['history']) >= 15 and zone_data and 'lines' in zone_data:
        # Check velocity vector
        past_point = state['history'][-15]
        vx = centroid[0] - past_point[1]
        vy = centroid[1] - past_point[2]
        # Extrapolate vector a bit
        p1 = centroid
        p2 = (centroid[0] + vx * 10, centroid[1] + vy * 10)
        
        for line in zone_data['lines']:
            if check_intersection(p1, p2, line[0], line[1]):
                # Ray intersects
                score = 85 # Predictive
                event_type = "Predictive Intrusion"
                explanation = f"{class_name.capitalize()} trajectory intersects with fence. (Probability > 80%)"
                if score > 100: score = 100
                state['last_score'] = score
                state['last_event'] = event_type
                if score > 50: state['last_alert_time'] = current_time
                return int(score), event_type, explanation
                
    # 5. Loitering
    # Check if object has been around for > x seconds and hasn't moved much
    if len(state['history']) >= 150: # Roughly 5 seconds at 30fps
        oldest_time = state['history'][-150][0]
        if current_time - oldest_time >= 5.0:
            # Check displacement
            old_c = (state['history'][-150][1], state['history'][-150][2])
            dist = math.hypot(centroid[0] - old_c[0], centroid[1] - old_c[1])
            if dist < 50: # arbitrary pixel threshold
                score = 40 * multiplier
                event_type = "Loitering"
                explanation = f"{class_name.capitalize()} loitering detected > 5s."
                if score > 100: score = 100
                state['last_score'] = score
                state['last_event'] = event_type
                if score > 50: state['last_alert_time'] = current_time
                return int(score), event_type, explanation
                
    score = 10
    state['last_score'] = score
    state['last_event'] = event_type
    return int(score), event_type, explanation
