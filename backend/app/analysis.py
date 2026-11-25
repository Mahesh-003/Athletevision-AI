"""Video-based squat screening. Heuristics are not a medical/safety assessment."""
from __future__ import annotations
import math
import os
from pathlib import Path
from urllib.request import urlretrieve
import cv2
import numpy as np

MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'
# MediaPipe pose indices
L_SHOULDER, R_SHOULDER = 11, 12
L_HIP, R_HIP = 23, 24
L_KNEE, R_KNEE = 25, 26
L_ANKLE, R_ANKLE = 27, 28
JOINTS = [(11,23),(23,25),(25,27),(12,24),(24,26),(26,28),(11,12),(23,24)]


def angle(a, b, c):
    a, b, c = [np.asarray(x, dtype=float) for x in (a,b,c)]
    ba, bc = a-b, c-b
    d = float(np.linalg.norm(ba)*np.linalg.norm(bc))
    if d < 1e-9: return None
    return round(math.degrees(math.acos(float(np.clip(np.dot(ba,bc)/d,-1,1)))),1)


def metrics(points):
    """Normalized 2D landmarks. Side chosen from mean visibility."""
    score_l = sum(points[i][2] for i in (L_SHOULDER,L_HIP,L_KNEE,L_ANKLE))
    score_r = sum(points[i][2] for i in (R_SHOULDER,R_HIP,R_KNEE,R_ANKLE))
    side = (L_SHOULDER,L_HIP,L_KNEE,L_ANKLE) if score_l >= score_r else (R_SHOULDER,R_HIP,R_KNEE,R_ANKLE)
    if min(points[i][2] for i in side) < .45: return None
    s,h,k,a = [points[i][:2] for i in side]
    knee = angle(h,k,a)
    torso = abs(math.degrees(math.atan2(s[0]-h[0], h[1]-s[1]))) if abs(h[1]-s[1])>.001 else 90
    return {'knee_angle':knee, 'torso_lean':round(torso,1), 'hip_y':round(h[1],3), 'knee_y':round(k[1],3), 'side':'left' if side[0]==L_SHOULDER else 'right'}


def classify(samples):
    """Screen only observable features; avoid universal biomechanics claims."""
    valid = [x for x in samples if x['metrics'] and x['metrics']['knee_angle'] is not None]
    if len(valid)<5:
        return {'status':'insufficient_data','reps':0,'issues':[{'type':'visibility','message':'Body landmarks were not consistently visible. Record a steady side-view video with your entire body visible.','timestamp':0}], 'metrics':{},'series':[]}
    angles = [x['metrics']['knee_angle'] for x in valid]
    # State transitions, with hysteresis to avoid counting noisy near-threshold frames.
    state='up'; reps=0; bottoms=[]; current_min=180; current_time=0
    for x in valid:
        val=x['metrics']['knee_angle']
        if state=='up' and val<125: state='down'; current_min=val; current_time=x['time']
        elif state=='down':
            if val<current_min: current_min=val; current_time=x['time']
            if val>155:
                reps+=1; bottoms.append({'minimum_knee_angle':round(current_min,1),'timestamp':round(current_time,2)});state='up'
    lean_values=[x['metrics']['torso_lean'] for x in valid]
    issues=[]
    if reps and any(b['minimum_knee_angle']>105 for b in bottoms):
        b=next(b for b in bottoms if b['minimum_knee_angle']>105)
        issues.append({'type':'limited_knee_flexion','message':'Some reps showed limited knee flexion. Review depth relative to your squat variation, anatomy, and training goal with a coach. Knee angle alone does not establish squat depth.','timestamp':b['timestamp']})
    if max(lean_values)>50:
        t=next(x['time'] for x in valid if x['metrics']['torso_lean']>50)
        issues.append({'type':'torso_inclination','message':'Large 2D torso inclination detected. Check camera view and compare against your chosen squat style; forward lean is not automatically incorrect.','timestamp':round(t,2)})
    if reps==0:
        issues.append({'type':'repetitions','message':'No complete squat repetition confidently detected. Ensure the recording includes both standing and bent-knee positions.','timestamp':0})
    return {'status':'review' if issues else 'no_screened_issue','reps':reps,'issues':issues, 'metrics':{'minimum_knee_angle':round(min(angles),1),'maximum_torso_lean':round(max(lean_values),1),'frames_with_pose':len(valid)},'series':[{'time':round(x['time'],2),'knee_angle':x['metrics']['knee_angle'],'torso_lean':x['metrics']['torso_lean']} for x in valid], 'rep_details':bottoms}


def get_model(model_dir:Path):
    model_dir.mkdir(parents=True,exist_ok=True)
    path=model_dir/'pose_landmarker_lite.task'
    if not path.exists():
        tmp=path.with_suffix('.download')
        try: urlretrieve(MODEL_URL,str(tmp)); tmp.replace(path)
        finally: tmp.unlink(missing_ok=True)
    return path


def analyze_video(input_path:Path, output_path:Path, model_dir:Path, yolo=False):
    import mediapipe as mp
    pose_path=get_model(model_dir)
    BaseOptions=mp.tasks.BaseOptions
    PoseLandmarker=mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions=mp.tasks.vision.PoseLandmarkerOptions
    RunningMode=mp.tasks.vision.RunningMode
    opts=PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(pose_path)),running_mode=RunningMode.VIDEO,num_poses=1,min_pose_detection_confidence=.5)
    cap=cv2.VideoCapture(str(input_path))
    fps=cap.get(cv2.CAP_PROP_FPS) or 25.0
    width,height=int(cap.get(3)),int(cap.get(4))
    if width<=0 or height<=0:
        cap.release();raise ValueError('Could not decode this video. Try MP4 (H.264).')
    # Processing at native fps can be expensive. Analyze at max 15fps but preserve all frames for video output.
    out=cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
    if not out.isOpened(): cap.release();raise RuntimeError('Video encoder unavailable')
    detector=None; yolo_warning=None
    if yolo:
        try:
            from ultralytics import YOLO
            detector=YOLO(os.getenv('YOLO_MODEL','yolo26n.pt'))
        except Exception as e: yolo_warning='YOLO unavailable: '+str(e)[:150]
    samples=[];last_points=None;last_measure=None; frame_no=0; pose_frames=0; last_ts=-1
    try:
        with PoseLandmarker.create_from_options(opts) as landmark:
            while True:
                ok, frame=cap.read()
                if not ok:break
                time_sec=frame_no/fps
                if frame_no%max(1,round(fps/15))==0:
                    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                    ts=max(last_ts+1,round(time_sec*1000)); last_ts=ts
                    result=landmark.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),ts)
                    if result.pose_landmarks:
                        p=result.pose_landmarks[0]
                        last_points=[(a.x,a.y,a.visibility if a.visibility is not None else 1.) for a in p]
                        last_measure=metrics(last_points)
                        if last_measure:pose_frames+=1
                    else: last_points=None;last_measure=None
                    samples.append({'time':time_sec,'metrics':last_measure})
                    if detector is not None and frame_no%max(1,round(fps))==0:
                        # Object detection included as optional integration, not assumed to track a barbell.
                        try: detector.predict(frame,verbose=False,conf=.4)
                        except Exception as e:
                            yolo_warning='YOLO inference unavailable: '+str(e)[:120];detector=None
                if last_points:
                    for j,k in JOINTS:
                        if min(last_points[j][2],last_points[k][2])>.45:
                            pa=(int(last_points[j][0]*width),int(last_points[j][1]*height))
                            pb=(int(last_points[k][0]*width),int(last_points[k][1]*height))
                            cv2.line(frame,pa,pb,(70,230,170),3,cv2.LINE_AA)
                    if last_measure:
                        cv2.putText(frame,f"Knee: {last_measure['knee_angle']} deg  Torso: {last_measure['torso_lean']} deg",(15,35),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),2)
                out.write(frame);frame_no+=1
                if frame_no>fps*180:break  # 3-minute cap
    finally:cap.release();out.release()
    if frame_no==0:raise ValueError('No readable frames in video')
    result=classify(samples)
    result['video']={'fps':round(fps,2),'duration_seconds':round(frame_no/fps,1),'width':width,'height':height,'pose_frames':pose_frames}
    if yolo_warning:result['yolo_warning']=yolo_warning
    return result
