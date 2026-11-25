"""Pixel-space geometry. Never compare normalized x/y angles without aspect correction."""
import math

CONNECTIONS = [(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),
               (23,24),(23,25),(25,27),(24,26),(26,28),(27,29),(29,31),
               (28,30),(30,32)]

def angle(a, b, c):
    """Angle ABC in degrees. Points are pixel coordinates."""
    u = (a[0]-b[0], a[1]-b[1])
    v = (c[0]-b[0], c[1]-b[1])
    den = math.hypot(*u)*math.hypot(*v)
    if den < 1e-7: return None
    cos = max(-1, min(1, (u[0]*v[0]+u[1]*v[1])/den))
    return math.degrees(math.acos(cos))

def torso_lean(shoulder, hip):
    """Approximate torso angle from image vertical. Camera rotation affects measurement."""
    dx = shoulder[0] - hip[0]
    dy = shoulder[1] - hip[1]
    return math.degrees(math.atan2(abs(dx), max(1e-6, abs(dy))))

def get_point(landmarks, idx, width, height, min_visibility=0.55):
    if not landmarks or idx >= len(landmarks): return None
    item=landmarks[idx]
    if item.get('visibility', 1) < min_visibility: return None
    return (item['x']*width, item['y']*height)

def feature(landmarks, width, height):
    """Prefer the more visible complete side; do not average occluded opposite sides."""
    best=None
    for shoulder,hip,knee,ankle,side in [(11,23,25,27,'left'),(12,24,26,28,'right')]:
        pts=[get_point(landmarks, x, width, height) for x in (shoulder,hip,knee,ankle)]
        if any(p is None for p in pts): continue
        s,h,k,a=pts
        ak=angle(h,k,a)
        ah=angle(s,h,k)
        if ak is None or ah is None:continue
        score=sum(landmarks[x].get('visibility',1) for x in (shoulder,hip,knee,ankle))
        value={'side':side,'knee_angle':round(ak,1),'hip_angle':round(ah,1),
            'torso_lean':round(torso_lean(s,h),1),
            'hip_y':h[1]/height,'knee_y':k[1]/height,'points':{'hip':h,'knee':k,'ankle':a,'shoulder':s}}
        if best is None or score > best[0]:best=(score,value)
    return best[1] if best else None
