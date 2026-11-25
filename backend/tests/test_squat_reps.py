from app.sports import squat


def frame(knee, hip_y, lean=17):
    return {'knee_angle': knee, 'hip_y': hip_y, 'knee_y': .55,
            'torso_lean': lean, 'hip_angle': 100}


def test_per_rep_timestamps_and_score():
    angles = [173,160,125,108,92,106,132,160,175]
    positions = [.42,.43,.5,.59,.66,.61,.53,.45,.42]
    result = squat([(i*.15, frame(a,y)) for i,(a,y) in enumerate(zip(angles,positions))])
    assert result['reps']==1
    e=result['events'][0]
    assert e['rep']==1
    assert e['start_s'] <= e['bottom_s'] < e['end_s']
    assert e['depth_review'] is False
    assert e['technique_score']==100
    assert e['checks'][0]['points_awarded']==50


def test_shallow_and_lean_rep_flags_and_feedback():
    angles = [175,160,120,100,87,110,135,160,174]
    result = squat([(i*.15,frame(a,.43 if a>130 else .48,55)) for i,a in enumerate(angles)])
    e=result['events'][0]
    assert e['technique_score']==20
    assert {f['code'] for f in e['findings']}=={'depth','torso'}
    assert all(f['correction'] for f in e['findings'])


def test_incomplete_cycle_not_counted():
    result=squat([(i*.2,frame(a,.48)) for i,a in enumerate([170,155,125,100,90,88])])
    assert result['reps']==0
    assert not result['events']
