"""Real original CPU WAV loudness -> Blender jaw animation -> independent reimport."""
import hashlib,io,json,math,struct,sys,wave
from pathlib import Path
from tempfile import TemporaryDirectory
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from forge.human_lipsync import build_human_lipsync
BINARY=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
if not BINARY.is_file():raise RuntimeError("owner installed Blender 5.2 required")
with TemporaryDirectory(prefix="mgr-human-audio-proof-") as scratch:
    temp=Path(scratch)
    buffer=io.BytesIO()
    rate=16000
    with wave.open(buffer,"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate)
        samples=[]
        for frame in range(rate*2):
            t=frame/rate
            if .25<t<1.65:
                tone=math.sin(2*math.pi*210*t)+.20*math.sin(2*math.pi*420*t)
                level=.45 if t<.83 else .62
                samples.append(round(30000*level*tone/1.2))
            else:samples.append(0)
        out.writeframes(struct.pack("<"+str(len(samples))+"h",*samples))
    wav=temp/"original-synthetic-audio.wav"
    wav.write_bytes(buffer.getvalue())
    receipt=build_human_lipsync({"actor_id":"mgr-audio-motion-pilot"},temp/"human-project",
                                 audio_wav=wav,blender=BINARY,fps=24)
    timeline=json.loads((temp/"human-project"/"phoneme-timeline"/"lipsync.json").read_text())
    if (receipt["source_wav_loudness_reactive"] is not True or
        timeline["audio_file_used"] is not True or
        timeline["automatic_audio_alignment_verified"] is not False or
        receipt["status"]!="GENERATED_AND_INDEPENDENTLY_REIMPORTED"):
        raise RuntimeError("false audio phoneme alignment or missing real Blender receipt")
    wav_hash=hashlib.sha256(wav.read_bytes()).hexdigest()
    if wav_hash!=receipt["source_audio_sha256"]:
        raise RuntimeError("WAV digest not bound to face output")
    safe={
     "schema":"mgr.forge.human-original-audio-motion-blender.v1",
     "date":"2026-11-01",
     "status":"REAL_PCM_TO_JAW_ANIMATION_INDEPENDENT_BLENDER_PASS",
     "synthetic_audio_only":True,
     "real_wav_sha256":wav_hash,
     "wav_sample_rate":rate,
     "output_glb_sha256":receipt["glb_sha256"],
     "output_glb_bytes":receipt["glb_bytes"],
     "morph_targets":receipt["morph_target_count"],
     "animation_actions":receipt["animation_actions"],
     "source_audio_consumed":True,
     "automatic_wav_loudness_driven_jaw":True,
     "automatic_phoneme_alignment":False,
     "speech_to_text_performed":False,
     "model_weights_downloaded":False,
     "Blender_independent_reimport":True,
     "owner_human_art_accepted":False,
     "voice_ownership_or_identity_inferred":False,
     "limits":["No phoneme or facial emotion recognition",
               "Only the mouth jaw energy responds to acoustic amplitude",
               "Actual own user speech would require separately approved source + consent"]
    }
    out=root/"evidence"/"human"/"2026-11-01-audio-reactive-face-blender.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError("do not overwrite original audio proof")
    out.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("MGR_REAL_AUDIO_FACE_BLENDER_PASS",json.dumps({"sha":receipt["glb_sha256"],"bytes":receipt["glb_bytes"],"jaw_activity_ratio":timeline["speech_activity_ratio_estimate"]}))
