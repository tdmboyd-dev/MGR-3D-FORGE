"""Optional external Blender import proof; never pretends Blender was run."""

import json
from pathlib import Path
import shutil
import subprocess


PROBE=Path(__file__).resolve().parent.parent/"bridge"/"blender_probe.py"
RENDER=Path(__file__).resolve().parent.parent/"bridge"/"blender_render.py"
SCENE_FACTS=Path(__file__).resolve().parent.parent/"bridge"/"blender_scene_facts.py"
RIG=Path(__file__).resolve().parent.parent/"bridge"/"blender_rig.py"
POSE_RENDER=Path(__file__).resolve().parent.parent/"bridge"/"blender_pose_render.py"


def blender_command(blender_binary,source,report):
    if not Path(source).is_file() or Path(source).suffix.lower()!=".glb":
        raise ValueError("a real GLB path is required")
    if not PROBE.is_file():
        raise FileNotFoundError("Blender verification script missing")
    return [str(blender_binary),"--background","--factory-startup",
            "--python",str(PROBE),"--",str(Path(source).resolve()),str(Path(report).resolve())]


def verify_blender(source,report,*,blender_binary="blender",timeout_seconds=120):
    """Only actual `bpy` import receipts count as Blender verification."""
    if shutil.which(str(blender_binary)) is None:
        raise RuntimeError("Blender executable unavailable; independent import NOT verified")
    command=blender_command(blender_binary,source,report)
    result=subprocess.run(command,timeout=timeout_seconds,capture_output=True,text=True,
                          check=False)
    if result.returncode:
        raise RuntimeError(f"Blender import failed (exit {result.returncode}): {result.stderr[-500:]}")
    data=json.loads(Path(report).read_text(encoding="utf-8"))
    if data.get("status")!="PASS" or data.get("triangles",0)<=0:
        raise RuntimeError("Blender verification receipt is invalid")
    return data


def blender_render_command(blender_binary,source,image,report):
    if not Path(source).is_file() or Path(source).suffix.lower()!=".glb":
        raise ValueError("a real GLB path is required")
    if Path(image).suffix.lower()!=".png":
        raise ValueError("render output must be PNG")
    if not RENDER.is_file():
        raise FileNotFoundError("Blender render script missing")
    return [str(blender_binary),"--background","--factory-startup",
            "--python",str(RENDER),"--",str(Path(source).resolve()),
            str(Path(image).resolve()),str(Path(report).resolve())]


def blender_facts_command(blender_binary,source,report):
    if not Path(source).is_file() or Path(source).suffix.lower()!=".glb":
        raise ValueError("a real GLB path is required")
    if not SCENE_FACTS.is_file():
        raise FileNotFoundError("Blender scene facts script missing")
    return [str(blender_binary),"--background","--factory-startup",
            "--python",str(SCENE_FACTS),"--",str(Path(source).resolve()),
            str(Path(report).resolve())]


def blender_rig_command(blender_binary,character_folder,blend_output,report,*,skin=False):
    if not (Path(character_folder)/"character.json").is_file():
        raise ValueError("character manifest required")
    if Path(blend_output).suffix.lower()!=".blend":
        raise ValueError("Blender project must end in .blend")
    if not RIG.is_file():
        raise FileNotFoundError("Blender rig assembly script missing")
    command=[str(blender_binary),"--background","--factory-startup",
            "--python",str(RIG),"--",str(Path(character_folder).resolve()),
            str(Path(blend_output).resolve()),str(Path(report).resolve())]
    return command+(["SKIN"] if skin else [])


def blender_pose_render_command(blender_binary,blend_source,first_image,second_image,report):
    if not Path(blend_source).is_file() or Path(blend_source).suffix.lower()!=".blend":
        raise ValueError("Blender project file required")
    if any(Path(image).suffix.lower()!=".png" for image in (first_image,second_image)):
        raise ValueError("pose renders must be PNG")
    if not POSE_RENDER.is_file():
        raise FileNotFoundError("Blender pose-render script missing")
    return [str(blender_binary),"--background","--factory-startup",
            "--python",str(POSE_RENDER),"--",str(Path(blend_source).resolve()),
            str(Path(first_image).resolve()),str(Path(second_image).resolve()),str(Path(report).resolve())]
