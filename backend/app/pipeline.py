import os, cv2, time, json, urllib.request
from pathlib import Path
import numpy as np
from .geometry import CONNECTIONS, feature
from .sports import squat, running

MODEL_URL='https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'models'/'pose_landmarker_lite.task'

def ensure_model():
    MODEL.parent.mkdir(parents=True,exist_ok=True)
    if not MODEL.exists():
        try: urllib.request.urlretrieve(MODEL_URL,MODEL)
        except Exception as e: raise RuntimeError(f'Could not download MediaPipe model: {e}') from e
    return MODEL

def analyze(src, dest, sport, use_yolo=False):
    import mediapipe as mp
    model=ensure_model()
    video=cv2.VideoCapture(str(src))
    if not video.isOpened():raise ValueError('Invalid or unsupported video.')
    fps=video.get(cv2.CAP_PROP_FPS)
    if not fps or fps<1 or fps>240:fps=30
    width=int(video.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if width<32 or height<32:video.release();raise ValueError('Invalid video dimensions.')
    if width>1280:
        scale=1280/width;width=int(width*scale);height=int(height*scale)
    sample_step=max(1,round(fps/12))
    out_fps=fps/sample_step
    writer=cv2.VideoWriter(str(dest),cv2.VideoWriter_fourcc(*'mp4v'),out_fps,(width,height))
    if not writer.isOpened():video.release();raise RuntimeError('Cannot initialize output video encoder.')
    yolo=None; yolo_error=None
    if use_yolo:
        try:
            from ultralytics import YOLO
            yolo=YOLO(os.getenv('YOLO_MODEL','yolo11n.pt'))
        except Exception as e:yolo_error=str(e)
    options=mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,num_poses=1,
        min_pose_detection_confidence=0.5,min_tracking_confidence=0.5)
    all_frames=[];running_frames=[];frame_index=0;sampled=0;start=time.monotonic()
    try:
        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
            while True:
                ok,frame=video.read()
                if not ok:break
                if frame_index%sample_step:
                    frame_index+=1;continue
                # Prevent unbounded processing time on huge videos.
                if sampled>=900:break
                frame=cv2.resize(frame,(width,height))
                rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                timestamp=max(0,round(frame_index*1000/fps))
                result=landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),timestamp)
                raw=[]; feat=None
                if result.pose_landmarks:
                    raw=[{'x':p.x,'y':p.y,'visibility':p.visibility} for p in result.pose_landmarks[0]]
                    feat=feature(raw,width,height)
                    for a,b in CONNECTIONS:
                        pa,pb=raw[a],raw[b]
                        if pa['visibility']>.5 and pb['visibility']>.5:
                            cv2.line(frame,(int(pa['x']*width),int(pa['y']*height)),
                                     (int(pb['x']*width),int(pb['y']*height)),(75,218,170),2)
                    for p in raw:
                        if p['visibility']>.5:cv2.circle(frame,(int(p['x']*width),int(p['y']*height)),3,(235,225,90),-1)
                if yolo:
                    # Only detects people using pretrained COCO categories; not barbell mechanics.
                    try:
                        track=yolo.track(frame,persist=True,classes=[0],verbose=False)[0]
                        for box in track.boxes:
                            x1,y1,x2,y2=map(int,box.xyxy[0].tolist())
                            cv2.rectangle(frame,(x1,y1),(x2,y2),(115,145,249),2)
                    except Exception as e:
                        yolo_error=str(e);yolo=None
                t=round(frame_index/fps,3)
                all_frames.append((t,feat))
                running_frames.append((t,feat,raw))
                cv2.rectangle(frame,(0,0),(width,54),(18,24,38),-1)
                label=f'{sport.upper()}  |  {t:.1f}s  |  '
                label+=f"Knee {feat['knee_angle']:.0f} deg   Torso {feat['torso_lean']:.0f} deg" if feat else 'Pose unavailable'
                cv2.putText(frame,label[:85],(12,34),cv2.FONT_HERSHEY_SIMPLEX,.58,(248,249,253),2,cv2.LINE_AA)
                writer.write(frame);sampled+=1;frame_index+=1
    finally:
        video.release();writer.release()
    if sampled==0:raise ValueError('No video frames could be decoded.')
    outcome=squat(all_frames) if sport=='squat' else running(running_frames,width,height)
    outcome['video']={'processed_frames':sampled,'sample_rate_fps':round(out_fps,2),'duration_s':round(frame_index/fps,2),
                      'output_may_need_browser_codec_conversion':True}
    outcome['tracking']={'yolo_requested':use_yolo,'yolo_active':bool(use_yolo and yolo_error is None),
                         'warning':yolo_error}
    outcome['series']=[{'time_s':t,'knee_angle':f['knee_angle'],'torso_lean':f['torso_lean']} for t,f in all_frames if f][::2]
    outcome['elapsed_seconds']=round(time.monotonic()-start,2)
    return outcome
