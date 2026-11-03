"""Existing Human Forge mannequin + original viseme timeline + Blender pipeline.

No arbitrary downloaded model, voice cloning, raw-speech alignment, or premium
skin/teeth inference. All output stays in a new directory with exact receipts.
"""
import hashlib,json,subprocess,math
from pathlib import Path
import shutil
from .character import build_mannequin
from .lipsync import create_lipsync_timeline
from .audio_motion import create_audio_motion_timeline

def _blender(binary,script,args,timeout=110):
    located=shutil.which(str(binary))
    if not located:
        raise RuntimeError("Real Blender executable required for facial rig; no fake inference")
    cmd=[located,"--background","--factory-startup","--python",
         str(Path(__file__).resolve().parents[1]/"bridge"/script),"--",*(str(x) for x in args)]
    try:
        result=subprocess.run(cmd,timeout=timeout,text=True,capture_output=True,stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Blender facial job timed out; inspect unmodified outputs") from error
    if result.returncode or "Traceback (most recent call last)" in result.stderr or (
            "Traceback (most recent call last)" in result.stdout):
        raise RuntimeError("Blender facial verification error: "+(result.stderr or result.stdout)[-900:])
    return result.stdout

def build_human_lipsync(spec,out,*,blender="blender",fps=24,audio_wav=None):
    target=Path(out)
    if target.exists():
        raise FileExistsError("human project already exists; preserve earlier asset")
    if not shutil.which(str(blender)):
        raise RuntimeError("Blender not installed or executable path invalid")
    target.mkdir(parents=True)
    mannequin=target/"existing-human-forge"
    build_mannequin(mannequin,"T")
    if audio_wav is None:
        timeline=create_lipsync_timeline(spec,target/"phoneme-timeline",fps=fps)
    else:
        source=Path(audio_wav)
        if source.is_symlink() or not source.is_file() or source.stat().st_size>20_000_000:
            raise ValueError("approved original PCM WAV file required")
        timeline=create_audio_motion_timeline(source.read_bytes(),target/"phoneme-timeline",
                    actor_id=spec["actor_id"],fps=fps)
    face=target/"facial-animation"
    try:
        s=_blender(blender,"blender_face_lipsync.py",[mannequin,target/"phoneme-timeline",face])
        if "MGR_HUMAN_FACIAL_EXPORT=" not in s:
            raise RuntimeError("Blender completed without emitting facial export receipt")
        verify=_blender(blender,"blender_face_reimport.py",[face])
        if "MGR_FACE_REIMPORT=" not in verify:
            raise RuntimeError("Second Blender process reported no independent facial proof")
        report=json.loads((face/"lipsync-blender-proof.json").read_text(encoding="utf8"))
        binary=(face/"human-lipsync.glb").read_bytes()
        if (report["status"]!="HUMAN_FACIAL_GLTF_REIMPORT_RENDER_PASS" or
            report.get("export_sha256")!=hashlib.sha256(binary).hexdigest() or
            report.get("gltf_morph_target_primitives",0)<6 or
            report.get("imported_animation_actions",0)<1 or
            not report.get("receiver_independently_reimported")):
            raise RuntimeError("Facial GLB lacks actual morph/animation reimport proof")
        expected_ranges={name:[min(frame['weights'][name] for frame in timeline['frames']),
                               max(frame['weights'][name] for frame in timeline['frames'])]
                         for name in timeline['channels']}
        observed=report.get('receiver_shape_key_ranges',{})
        if (report.get('timeline_source_sha256')!=timeline['source_input_sha256'] or
            report.get('receiver_evaluated_geometry_verified') is not True or
            report.get('receiver_animation_fps')!=fps or
            report.get('receiver_evaluated_frames')!=len(timeline['frames']) or
            type(report.get('receiver_evaluated_vertices')) is not int or
            report['receiver_evaluated_vertices']<1 or
            set(observed)!=set(expected_ranges)):
            raise RuntimeError('Facial receiver missing source-bound evaluated animation proof')
        for name,expected in expected_ranges.items():
            values=observed[name]
            if not isinstance(values,list) or len(values)!=2 or any(
                    type(v) not in (int,float) or not math.isfinite(v) or abs(v-e)>2e-4
                    for v,e in zip(values,expected)):
                raise RuntimeError('Imported facial animation differs from original authored timeline')
        expected_motion=any(high-low>1e-4 for low,high in expected_ranges.values())
        expected_shape=any(high>1e-4 for _,high in expected_ranges.values())
        for key,required in [('receiver_max_vertex_motion_m',expected_motion),
                             ('receiver_max_shape_response_m',expected_shape)]:
            value=report.get(key)
            if type(value) not in (int,float) or not math.isfinite(value) or value<0 or (required and value<=1e-6):
                raise RuntimeError('Imported facial keys failed independent mesh deformation proof')
        result={"schema":"mgr.forge.human-lipsync-acceptance.v1",
                "status":"GENERATED_AND_INDEPENDENTLY_REIMPORTED",
                "actor_id":spec["actor_id"],
                "existing_human_source_path":"existing-human-forge/mannequin.glb",
                "timeline_path":"phoneme-timeline/lipsync.json",
                "editable_blender_path":"facial-animation/human-lipsync.blend",
                "animation_glb_path":"facial-animation/human-lipsync.glb",
                "facial_preview_path":"facial-animation/human-lipsync-preview.png",
                "glb_sha256":report["export_sha256"],
                "glb_bytes":len(binary),
                "morph_target_count":report["gltf_morph_target_primitives"],
                "animation_actions":report["imported_animation_actions"],
                "timeline_fps":fps,"phoneme_events":len(timeline["events"]),
                "receiver_evaluated_animation_verified":True,
                "receiver_max_vertex_motion_m":report['receiver_max_vertex_motion_m'],
                "receiver_max_shape_response_m":report['receiver_max_shape_response_m'],
                "caller_supplied_timed_phonemes":audio_wav is None,
                "source_wav_loudness_reactive":audio_wav is not None,
                "source_audio_sha256":timeline["source_input_sha256"] if audio_wav is not None else None,
                "raw_audio_alignment_performed":False,"photoreal_human":False,
                "identity_approved":False,"owner_visual_quality_approved":False,
                "paid_gpu_or_cloud_used":False}
        (target/"human-lipsync-receipt.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        return result
    except Exception:
        # Keep forensic outputs and inputs instead of silently reporting success
        (target/"needs-reconciliation.txt").write_text("Blender face job incomplete; inspect source and saved outputs.\n")
        raise
