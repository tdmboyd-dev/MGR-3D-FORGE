"""Standalone MGR creature rig pipeline via local Blender.

Python owns source hash/receipts and fail-closed invocation, Blender owns 3D
armature/mesh skinning and independent receiving-import verification.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from .creature_rig_recipe import save_creature_rig_recipe


def _run_blender(binary, script, args, timeout):
    command=[str(binary),"--background","--factory-startup","--python",
             str(Path(__file__).resolve().parent.parent/"bridge"/script),"--",
             *[str(value) for value in args]]
    try:
        proc=subprocess.run(command,timeout=timeout,capture_output=True,text=True)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Blender operation timed out; reconcile partial outputs") from error
    # Blender occasionally exits zero on Python exceptions. Require a
    # structured result marker AND later read-back of the exact saved files.
    if proc.returncode!=0 or "Traceback (most recent call last)" in proc.stderr or (
            "Traceback (most recent call last)" in proc.stdout):
        raise RuntimeError("Blender reported an error; inspect preserved outputs")
    return proc.stdout


def rig_creature(source,output,*,blender="blender",timeout=180):
    src,out=Path(source),Path(output)
    if not (src/"creature.glb").is_file() or not (src/"creature.json").is_file():
        raise ValueError("source must have a real MGR original creature GLB and DNA")
    if out.exists():
        raise FileExistsError("will not overwrite an existing rig output")
    if not shutil.which(str(blender)):
        raise RuntimeError("Blender 5.x executable not found")
    with TemporaryDirectory(prefix="mgr-creature-rig-",dir=src.parent) as directory:
        staged=Path(directory)
        shutil.copyfile(src/"creature.glb",staged/"creature.glb")
        shutil.copyfile(src/"creature.json",staged/"creature.json")
        recipe=save_creature_rig_recipe(staged/"creature.json",
                                        staged/"rig-blueprint.json")
        initial=_run_blender(blender,"blender_creature_skin.py",[staged,out],timeout)
        if "MGR_CREATURE_SKIN=" not in initial:
            raise RuntimeError("Blender emitted no rigging execution receipt")
    # The exported GLB and scene survive even if the second import fails;
    # this unknown outcome cannot be relabeled production-ready.
    check=_run_blender(blender,"blender_creature_reimport.py",[out],timeout)
    if "MGR_CREATURE_REOPEN=" not in check:
        raise RuntimeError("receiving Blender emitted no independent import proof")
    path=out/"skin-proof.json"
    receipt=json.loads(path.read_text(encoding="utf-8"))
    glb=out/"creature-rigged.glb"
    if (receipt.get("status")!="LOCAL_BLENDER_REIMPORT_AND_RENDER_PASS" or
        receipt.get("mesh_source_sha256")!=recipe["mesh_sha256"] or
        receipt.get("reimported_armature_bones")!=recipe["bones"] or
        receipt.get("reimported_animation_actions",0)<1 or
        receipt.get("max_evaluated_vertex_motion_m",0)<.01 or
        receipt.get("rigged_glb_sha256")!=hashlib.sha256(glb.read_bytes()).hexdigest()):
        raise RuntimeError("rig proof lacks valid receiving-import or animation")
    return receipt
