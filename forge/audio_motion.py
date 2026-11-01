"""MGR Human Forge original CPU audio-reactive facial curves from real PCM WAV.

This is automatic LOUDNESS driven jaw motion. It is NOT speech recognition,
phoneme aligner, AI voice cloning, FACS inference or reliable vowel mouth sync.
Rhubarb/Audio2Face require separately licensed/proved adapters.
"""
from array import array
from collections.abc import Mapping
import hashlib,io,json,math,sys,wave,struct
from pathlib import Path
from .lipsync import CHANNELS

MAX_WAV_BYTES=20_000_000
MAX_AUDIO_MS=120_000

def _validate_actor(value):
    if not isinstance(value,str) or not 1<=len(value)<=80 or not all(
           c.isascii() and (c.isalnum() or c in "-_") for c in value):
        raise ValueError("invalid MGR actor label")
    return value

def _wav_features(blob):
    if not isinstance(blob,bytes) or not 44<=len(blob)<=MAX_WAV_BYTES:
        raise ValueError("WAV is missing or outside 20MB bound")
    if not blob.startswith(b"RIFF") or blob[8:12]!=b"WAVE":
        raise ValueError("Only standard RIFF/WAVE accepted")
    try:
        with wave.open(io.BytesIO(blob),"rb") as audio:
            channels=audio.getnchannels()
            rate=audio.getframerate()
            width=audio.getsampwidth()
            frames=audio.getnframes()
            if audio.getcomptype()!="NONE" or width!=2 or channels not in (1,2) or not 8000<=rate<=48000:
                raise ValueError("Input must be uncompressed PCM16 mono/stereo 8-48kHz")
            duration_ms=int(round(frames*1000/rate))
            if not 100<=duration_ms<=MAX_AUDIO_MS or frames*channels*2>MAX_WAV_BYTES:
                raise ValueError("Audio duration/expanded samples exceeded")
            frame_samples=max(1,round(rate*.04))
            levels=[]
            for index in range(0,frames,frame_samples):
                data=audio.readframes(min(frame_samples,frames-index))
                if len(data)%2 or not data:
                    raise ValueError("Truncated WAV samples")
                values=array("h")
                values.frombytes(data)
                if sys.byteorder!="little":values.byteswap()
                if channels==2 and len(values)%2:
                    raise ValueError("Stereo WAV data incomplete")
                # RMS pressure normalized to [-1..1]. Keep actual audio private.
                energy=sum(int(n)*int(n) for n in values)
                rms=math.sqrt(energy/len(values))/32768
                levels.append(rms)
    except (EOFError,wave.Error,struct.error) as error:
        raise ValueError("Malformed PCM WAV") from error
    if not levels:raise ValueError("No WAV audio samples")
    return levels,rate,duration_ms

def struct_error_proxy():
    # Exposes built-in struct error as a safe exception; import lazily to
    # avoid arbitrary binary parser dependencies.
    import struct
    return struct.error

def create_audio_motion_timeline(wav_bytes, output, *, actor_id="mgr-generic-human", fps=24):
    """Convert caller-approved WAV bytes into visible 3D mouth opening curves.

    Source has NO trained phoneme model. Emit a full eight-channel curve schema
    compatible with existing Human Forge / Blender bridge, but only jawOpen
    and a weak mouthWide follow the source audio envelope.
    """
    actor=_validate_actor(actor_id)
    if type(fps) is not int or not 12<=fps<=60:
        raise ValueError("fps outside 12..60")
    levels,rate,duration_ms=_wav_features(wav_bytes)
    target=Path(output)
    if target.exists():
        raise FileExistsError("Do not overwrite original audio/reactive model")
    ordered=sorted(levels)
    floor=ordered[max(0,int(.14*(len(ordered)-1)))]
    high=ordered[max(0,int(.94*(len(ordered)-1)))]
    span=max(.006,high-floor)
    smoothed=0.0
    frames=[]
    total=math.ceil(duration_ms*fps/1000)+1
    for i in range(total):
        t=min(duration_ms,round(i*1000/fps))
        ix=min(len(levels)-1,max(0,int(t/40)))
        # Avoid a hard jaw edge on background room noise. Do not assume
        # loud noise means a voiced phoneme or known human speaker.
        normalized=max(0.0,min(1.0,(levels[ix]-floor-.014)/span))
        alpha=.58 if normalized>smoothed else .20
        smoothed+=alpha*(normalized-smoothed)
        if smoothed<.08:smoothed=0.0
        jaw=min(1.0,smoothed*.87)
        weights={name:0.0 for name in CHANNELS}
        weights["jawOpen"]=round(jaw,5)
        weights["mouthWide"]=round(jaw*.17,5)
        frames.append({"frame":i+1,"time_ms":t,"weights":weights})
    target.mkdir(parents=True)
    source_sha=hashlib.sha256(wav_bytes).hexdigest()
    ratio=round(sum(f["weights"]["jawOpen"]>.12 for f in frames)/len(frames),4)
    result={
     "schema":"mgr.forge.viseme-curves.v1",
     "status":"AUDIO_REACTIVE_NOT_PHONEME_ALIGNED",
     "actor_id":actor,"source_input_sha256":source_sha,
     "fps":fps,"duration_ms":duration_ms,"channels":list(CHANNELS),
     "events":[],"frames":frames,
     "audio_file_used":True,"speech_to_text_used":False,
     "automatic_audio_alignment_verified":False,
     "raw_audio_source_sha256":source_sha,"wave_sample_rate":rate,
     "speech_activity_ratio_estimate":ratio,
     "real_3d_shape_keys_verified":False,
     "reaction_type":"rms-enveloped-jaw-not-speech-phoneme-recognition",
     "limitations":["Sound pressure drives jawOpen; precise lip sync/vowels not recognized",
                    "Music/noise can also trigger motion",
                    "No face/identity, emotional performance or audio consent inferred",
                    "3D deformation and playback require Blender and owner review"]
    }
    (target/"lipsync.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return result
