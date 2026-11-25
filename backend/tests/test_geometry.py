from app.geometry import angle,torso_lean
from app.sports import squat,empty

def test_right_angle():
    assert round(angle((0,1),(0,0),(1,0)))==90

def test_vertical_torso():
    assert round(torso_lean((2,0),(2,4)))==0

def test_no_frames():
    assert squat([])['assessment']=='Insufficient evidence'

def test_rep_hysteresis():
    data=[]
    for i,knee in enumerate([175,160,125,110,98,115,140,159,175]):
        data.append((i*.1,{'knee_angle':knee,'torso_lean':15,'hip_y':.48 if knee>140 else .7,'knee_y':.55,'hip_angle':100}))
    assert squat(data)['reps']==1
