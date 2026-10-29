"""Offline pretrained vision and speech. Produces reviewable observations, not certified refereeing."""
import hashlib
import json
import math
import gc
import os
from pathlib import Path

MODEL_DIR=Path(__file__).resolve().parent/'models'
PROFILES={'eco':(2,384,2),'balanced':(4,512,4),'detail':(6,640,4)}

def video_digest(path):
    # Hash in chunks rather than loading an entire video into RAM.
    with open(path,'rb') as source:return hashlib.file_digest(source,'sha256').hexdigest()

def download_models(progress=lambda x:None):
    """Explicit first-run download; subsequent inference is offline."""
    from ultralytics import YOLO
    import urllib.request, zipfile
    MODEL_DIR.mkdir(exist_ok=True)
    for name in ['yolo11n.pt','yolo11n-pose.pt']:
        progress('Downloading / checking '+name)
        model=YOLO(str(MODEL_DIR/name))
        del model
    target=MODEL_DIR/'vosk-model-small-en-us-0.15'
    if not target.exists():
        progress('Downloading the English speech model (about 40 MB)…')
        archive=MODEL_DIR/'speech.zip'
        urllib.request.urlretrieve('https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',archive)
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                if not (MODEL_DIR/member.filename).resolve().is_relative_to(MODEL_DIR.resolve()): raise ValueError('Unsafe model archive path.')
            z.extractall(MODEL_DIR)
        archive.unlink()
    progress('Models ready. Local inference can now work offline.')

def transcribe(path):
    import subprocess, tempfile, wave
    import imageio_ffmpeg
    from vosk import Model, KaldiRecognizer, SetLogLevel
    SetLogLevel(-1)
    model_path=MODEL_DIR/'vosk-model-small-en-us-0.15'
    if not model_path.exists(): raise ValueError('Download models in Settings first.')
    with tempfile.TemporaryDirectory() as tmp:
        wav=Path(tmp)/'audio.wav'
        proc=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-i',str(path),'-t','30','-vn','-ar','16000','-ac','1',str(wav)],capture_output=True)
        if proc.returncode: raise ValueError('No readable audio track. Record with microphone enabled.')
        rec=KaldiRecognizer(Model(str(model_path)),16000); rec.SetWords(True); words=[]
        with wave.open(str(wav),'rb') as source:
            while chunk:=source.readframes(4000):
                if rec.AcceptWaveform(chunk): words.extend(json.loads(rec.Result()).get('result',[]))
        words.extend(json.loads(rec.FinalResult()).get('result',[]))
    return words

def distance(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def inside(p,rect):
    return bool(rect and rect[0]<=p[0]<=rect[2] and rect[1]<=p[1]<=rect[3])

def analyze_local(path,game,players,turn_player,context,calibration,progress=lambda value:None,profile='balanced'):
    import cv2
    path=Path(path); cap=cv2.VideoCapture(str(path))
    fps=cap.get(cv2.CAP_PROP_FPS); total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not cap.isOpened() or fps<=0 or total<=0: raise ValueError('Cannot decode this video. Use an MP4 recording.')
    duration=min(total/fps,300); cap.release()
    if total/fps>300: raise ValueError('Use a clip no longer than five minutes.')
    report={'game':game,'status':'uncertain','duration_seconds':duration,'summary':'Local observations require host review.','events':[],'possession':[],
      'limitations':['Pretrained models plus experimental rules; fixed camera required. Host must review every proposed event. No custom model training or accuracy claim.'],
      'video_sha256':video_digest(path),'model':'YOLO11n / Vosk offline','roster':players,'turn_player':turn_player,'host_context':context,'calibration':calibration,'review_required':True}
    def event(kind,t,evidence,confidence=.80,player=None):
        report['events'].append({'kind':kind,'player':player or turn_player,'time':round(t,2),'confidence':confidence,'evidence':evidence})
    words=[]
    if game in ['Family Story Relay','Falcon Freeze']:
        progress(5); words=transcribe(path)
        report['transcript']=' '.join(w['word'] for w in words)
    if game=='Family Story Relay':
        # Speech recognition supplies word evidence. Human checks sentence coherence and turn ownership.
        used=set()
        for w in words:
            word=w['word'].lower()
            if word in ('family','desert','kindness') and word not in used and w['end']<=30:
                used.add(word); snippet=' '.join(x['word'] for x in words if abs(x['start']-w['start'])<3)
                event('valid_sentence',w['start'],'Recognized assigned word '+word+' in: '+snippet+'. Host must verify a distinct coherent sentence.',min(.95,max(.75,w.get('conf',.75))))
        report['summary']='Offline speech recognized '+str(len(used))+' assigned words. Review the transcript and sentence rules before scoring.'
        progress(100); return report
    pose=game in ['Falcon Freeze','Dune Steps']
    name='yolo11n-pose.pt' if pose else 'yolo11n.pt'
    if not (MODEL_DIR/name).exists(): raise ValueError('Download local models in Settings first.')
    sample_fps,image_size,threads=PROFILES.get(profile,PROFILES['balanced'])
    stride=max(1,int(fps/sample_fps)); tracks={}; samples=[]; observations=[]; last_ball=None; last_owner=None; zone_lock=None; last_event=-10; target_index=0; last_marker=None
    seeds=calibration.get('players',{})
    if game=='Football' and set(seeds)!=set(players): raise ValueError('Calibrate each player’s starting position before local football analysis. All players must be visible at the beginning.')
    for p,xy in seeds.items(): tracks[p]=tuple(xy)
    goals=calibration.get('goals',{})
    if game=='Football' and not all(t in goals for t in set(players.values())): raise ValueError('Calibrate both goal rectangles. Each goal is labelled by the team that SCORES there.')
    if game=='Dune Steps' and len(calibration.get('markers',{}))!=3: raise ValueError('Calibrate all three floor markers first.')
    if game=='Majlis Delivery' and 'delivery' not in calibration: raise ValueError('Calibrate the delivery target rectangle first.')
    max_time=duration if game=='Football' else min(duration,30)
    # Speech-only turns never import PyTorch. Vision loads a single nano model.
    from ultralytics import YOLO
    import numpy as np
    import torch
    torch.set_num_threads(min(threads,os.cpu_count() or 1))
    model=YOLO(str(MODEL_DIR/name));cap=cv2.VideoCapture(str(path));decoded=-1
    report['performance_profile']=profile
    try:
        for frame_no in range(0,int(max_time*fps),stride):
            # Decode sequentially, avoiding repeated expensive seeks into compressed video.
            ok=True
            while decoded<frame_no:
                ok=cap.grab();decoded+=1
                if not ok:break
            if not ok:break
            ok,frame=cap.retrieve()
            if not ok:break
            t=frame_no/fps; h,w=frame.shape[:2]
            result=model.predict(frame,conf=.25,imgsz=image_size,max_det=20,verbose=False,device='cpu')[0]
            detections=[]; balls=[]
            for i,box in enumerate(result.boxes):
                cls=int(box.cls[0]); x1,y1,x2,y2=(box.xyxy[0].cpu().numpy()/np.array([w,h,w,h])).tolist()
                if cls==0: detections.append((i,((x1+x2)/2,(y1+y2)/2),(x1,y1,x2,y2),float(box.conf[0])))
                elif cls==32: balls.append((((x1+x2)/2,(y1+y2)/2),float(box.conf[0])))
            assigned={}; available=list(detections)
            if game=='Football':
                # One-to-one nearest-neighbour identities, anchored by host calibration.
                pairs=sorted((distance(xy,d[1]),p,k) for p,xy in tracks.items() for k,d in enumerate(available))
                used_p=set();used_d=set()
                for dist,p,k in pairs:
                    if dist<.18 and p not in used_p and k not in used_d:
                        assigned[p]=available[k];used_p.add(p);used_d.add(k)
                for p,d in assigned.items(): tracks[p]=d[1]
            elif detections: assigned[turn_player]=max(detections,key=lambda d:(d[2][2]-d[2][0])*(d[2][3]-d[2][1]))
            ball=max(balls,key=lambda b:b[1])[0] if balls else None
            if game=='Football':
                owner=None
                if ball and assigned:
                    candidates=[(distance(ball,((d[2][0]+d[2][2])/2,d[2][3])),p) for p,d in assigned.items()]
                    dist,nearest=min(candidates)
                    if dist<.16: owner=nearest
                if owner: samples.append({'player':owner,'start':round(t,3),'end':round(min(t+stride/fps,max_time),3),'confidence':.78})
                if ball:
                    current_zone=next((team for team,rect in goals.items() if inside(ball,rect)),None)
                    if current_zone and not zone_lock and last_ball is not None and last_owner and t-last_event>2:
                        scorer=last_owner if players[last_owner]==current_zone else next(p for p in players if players[p]==current_zone)
                        event('goal',t,'Ball centre entered calibrated goal zone for team '+current_zone+'. Verify whole-ball line crossing; scorer attribution is approximate.',.78,scorer);last_event=t
                    zone_lock=current_zone;last_ball=ball
                else: zone_lock=None;last_ball=None
                if owner: last_owner=owner
            elif game=='Dune Steps' and assigned and target_index<6:
                d=assigned[turn_player]; foot=((d[2][0]+d[2][2])/2,d[2][3]); i=d[0]
                if result.keypoints is not None:
                    points=result.keypoints.data[i].cpu().numpy()
                    ankles=[(x/w,y/h) for x,y,c in points[15:17] if c>.5]
                    if ankles: foot=min(ankles,key=lambda a:min(distance(a,xy) for xy in calibration['markers'].values()))
                dist,marker=min((distance(foot,xy),name) for name,xy in calibration['markers'].items())
                if dist<.10 and marker!=last_marker:
                    expected=str([1,3,2,1,2,3][target_index]); kind='correct_step' if marker==expected else 'wrong_step'
                    event(kind,t,'Detected foot near marker '+marker+'; expected '+expected+'. Host checks actual contact.')
                    if kind=='correct_step': target_index+=1
                    last_marker=marker
                elif dist>.14: last_marker=None
            elif game=='Majlis Delivery' and ball:
                active=inside(ball,calibration['delivery'])
                if active and not zone_lock and last_ball is not None and t-last_event>2:
                    event('delivery',t,'Detected sports ball entering delivery zone. Host must verify tray support and successful delivery.');last_event=t
                zone_lock=active; last_ball=ball
            elif game=='Falcon Freeze' and assigned:
                d=assigned[turn_player]; i=d[0]
                if result.keypoints is not None:
                    points=result.keypoints.data[i].cpu().numpy(); observations.append((t,[(float(x/w),float(y/h),float(c)) for x,y,c in points]))
            progress(min(95,int(10+85*t/max_time)))
    finally:
        cap.release();model=None;gc.collect()
    if game=='Falcon Freeze':
        for cue in [x for x in words if x['word']=='freeze' and x['end']+3<=max_time]:
            window=[v for t,v in observations if cue['end']+.3<=t<=cue['end']+3]
            if len(window)<max(3,int(2.0*fps/stride)): continue
            motion=[]
            for a,b in zip(window,window[1:]):
                ds=[distance(x[:2],y[:2]) for x,y in zip(a,b) if x[2]>.5 and y[2]>.5]
                if ds: motion.append(float(np.median(ds)))
            if motion:
                moved=max(motion)>(.025*stride/fps*6); event('freeze_movement' if moved else 'freeze_success',cue['end']+3,'Audio FREEZE cue followed by pose displacement '+str(round(max(motion),4))+'. Host checks camera stability and body movement.')
    # Merge consecutive possession observations from the same estimated identity.
    for s in samples:
        if report['possession'] and report['possession'][-1]['player']==s['player'] and abs(report['possession'][-1]['end']-s['start'])<.003: report['possession'][-1]['end']=s['end']
        else: report['possession'].append(s)
    report['summary']=f'Offline AI found {len(report["events"])} candidate events. Review the footage and player identities before applying.'
    report['limitations']+=['Identity uses nearest-neighbour tracking and can switch during crossings. Goal-zone entry is a candidate, not proof of whole-ball goal-line crossing.','Local delivery mode detects sports balls and does not automatically verify tray support or drops.','English speech only. Pose movement depends on a fixed camera and visible body.']
    progress(100);return report
