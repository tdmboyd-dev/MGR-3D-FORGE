"""Optional external Blender import proof; never pretends Blender was run."""

import json
from pathlib import Path
import shutil
import subprocess


PROBE=Path(__file__).resolve().parent.parent/"bridge"/"blender_probe.py"
RENDER=Path(__file__).resolve().parent.parent/"bridge"/"blender_render.py"
SCENE_FACTS=Path(__file__).resolve().parent.parent/"bridge"/"blender_scene_facts.py"


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
