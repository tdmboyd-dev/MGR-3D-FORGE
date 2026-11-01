"""Human Forge: original, bounded phoneme-to-viseme animation timeline.

Consumes caller-supplied aligned phonemes; no microphone, speech-to-text, audio
model, speaker identity inference, or lip-sync-from-raw-waveform is claimed.
The timeline controls an existing MGR mannequin's Blender face shape keys.
"""
import hashlib
import json
import math
from pathlib import Path

SCHEMA="mgr.forge.phoneme-timeline.v1"
CHANNELS=("jawOpen","mouthWide","mouthFunnel","mouthPucker","mouthSmile",
          "lipsPress","tongueOut","mouthShrug")
PHONEMES={
    "AA":"open","AE":"wide","AH":"open","AO":"round","AW":"round",
    "AX":"open","AXR":"open","EH":"wide","ER":"round","EY":"wide",
    "IH":"wide","IY":"wide","OW":"round","OY":"round","UH":"round","UW":"round",
    "B":"press","M":"press","P":"press","F":"press","V":"press",
    "TH":"tongue","DH":"tongue","L":"tongue",
    "CH":"funnel","JH":"funnel","SH":"funnel","ZH":"funnel",
    "R":"pucker","W":"pucker","Y":"wide",
    "D":"rest","T":"rest","N":"rest","S":"rest","Z":"rest","K":"rest",
    "G":"rest","HH":"rest","NG":"rest","SIL":"rest","PAUSE":"rest"
}
SHAPES={
    "rest":{},
    "open":{"jawOpen":0.82,"mouthWide":0.22},
    "wide":{"jawOpen":0.35,"mouthWide":0.8},
    "round":{"jawOpen":0.4,"mouthFunnel":0.78},
    "pucker":{"mouthPucker":0.86,"jawOpen":0.12},
    "press":{"lipsPress":0.9},
    "tongue":{"tongueOut":0.73,"jawOpen":0.3},
    "funnel":{"mouthFunnel":0.7,"jawOpen":0.2}
}
MAX_EVENTS=1000
MAX_DURATION_MS=120_000

def _validate(spec):
    if not isinstance(spec,dict) or set(spec)!={"schema","duration_ms","language","phonemes","actor_id"}:
        raise ValueError("timeline requires exact schema, actor, duration, language and timed phonemes")
    if spec["schema"]!=SCHEMA or spec["language"]!="en-US":
        raise ValueError("only explicit en-US phonemes are currently supported")
    actor=spec["actor_id"]
    if not isinstance(actor,str) or not 1<=len(actor)<=80 or not all(
          c.isascii() and (c.isalnum() or c in "-_") for c in actor):
        raise ValueError("invalid actor identifier")
    duration=spec["duration_ms"]
    if type(duration) is not int or not 100<=duration<=MAX_DURATION_MS:
        raise ValueError("invalid timeline duration")
    items=spec["phonemes"]
    if not isinstance(items,list) or not 1<=len(items)<=MAX_EVENTS:
        raise ValueError("timeline requires 1..1000 phoneme events")
    previous=0
    normalized=[]
    for item in items:
        if not isinstance(item,dict) or set(item)!={"phoneme","start_ms","end_ms"}:
            raise ValueError("phoneme must have exactly name and start/end milliseconds")
        name,start,end=item["phoneme"],item["start_ms"],item["end_ms"]
        if not isinstance(name,str) or name not in PHONEMES or type(start) is not int or type(end) is not int:
            raise ValueError("unknown phoneme or timing")
        if start<previous or end<=start or end>duration:
            raise ValueError("phoneme order overlap, missing duration or invalid time")
        previous=end
        normalized.append({"phoneme":name,"start_ms":start,"end_ms":end})
    return normalized,duration

def _weights_at(events,time_ms):
    # Join at the closest event center, fading in/out across the entire segment
    # so generated mouth targets do not jump between close phonemes.
    weights={k:0.0 for k in CHANNELS}
    for event in events:
        shape=SHAPES[PHONEMES[event["phoneme"]]]
        start,end=event["start_ms"],event["end_ms"]
        if not (start-55<=time_ms<=end+55):
            continue
        length=end-start
        fade=max(28.0,min(100.0,length*.30))
        up=min(1.0,max(0.0,(time_ms-start+55)/fade))
        down=min(1.0,max(0.0,(end+55-time_ms)/fade))
        strength=min(up,down)
        for channel,value in shape.items():
            weights[channel]=max(weights[channel],value*strength)
    # Strong articulations should not produce extreme overlapping jaw/corner distortion.
    if weights["lipsPress"]>.5:
        weights["jawOpen"]*=.30
    if weights["mouthPucker"]>.5:
        weights["mouthWide"]*=.25
    return {k:round(min(max(v,0.0),1.0),5) for k,v in weights.items()}

def create_lipsync_timeline(spec,output,*,fps=24):
    events,duration=_validate(spec)
    if type(fps) is not int or not 12<=fps<=60:
        raise ValueError("fps must be 12..60")
    target=Path(output)
    if target.exists():
        raise FileExistsError("never overwrite an existing audio/phoneme job")
    target.mkdir(parents=True)
    frames=[]
    total=math.ceil(duration*fps/1000)+1
    if total>7202:raise ValueError("too many animation frames")
    for i in range(total):
        t=min(duration,round(i*1000/fps))
        frames.append({"frame":i+1,"time_ms":t,"weights":_weights_at(events,t)})
    digest=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
    result={"schema":"mgr.forge.viseme-curves.v1",
            "status":"EXPLICIT_PHONEME_TIMING_NO_AUDIO_ALIGNMENT",
            "actor_id":spec["actor_id"],"source_input_sha256":digest,
            "fps":fps,"duration_ms":duration,"channels":list(CHANNELS),
            "events":events,"frames":frames,
            "audio_file_used":False,"speech_to_text_used":False,
            "automatic_audio_alignment_verified":False,"real_3d_shape_keys_verified":False,
            "claims":["timed cue interpolation","bounded coarticulation","original MGR expression curve output"],
            "limitations":["Requires externally supplied timing; not audio-to-lipsync AI",
                           "Blender animated facial mesh and visual correctness need independent verification"]}
    (target/"lipsync.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return result
