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
POSE_INSPECT=Path(__file__).resolve().parent.parent/"bridge"/"blender_pose_inspect.py"
CINEMATIC=Path(__file__).resolve().parent.parent/"bridge"/"blender_cinematic.py"
MATERIAL_INSPECT=Path(__file__).resolve().parent.parent/"bridge"/"blender_material_inspect.py"
DIRECTOR_INSPECT=Path(__file__).resolve().parent.parent/"bridge"/"blender_director_inspect.py"
DIRECTOR_FRAMES=Path(__file__).resolve().parent.parent/"bridge"/"blender_director_frames.py"
FX_RENDER=Path(__file__).resolve().parent.parent/"bridge"/"blender_fx_render.py"
STUDIO_WITNESS=Path(__file__).resolve().parent.parent/"bridge"/"blender_studio_witness.py"


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


def blender_pose_inspect_command(blender_binary, blend_source, observation_path):
    if not Path(blend_source).is_file() or Path(blend_source).suffix.lower() != ".blend":
        raise ValueError("existing Blender project required")
    if Path(observation_path).suffix.lower() != ".json":
        raise ValueError("observation output must be JSON")
    if not POSE_INSPECT.is_file():
        raise FileNotFoundError("Blender pose inspection script missing")
    return [str(blender_binary), "--background", "--factory-startup",
            "--python", str(POSE_INSPECT), "--", str(Path(blend_source).resolve()),
            str(Path(observation_path).resolve())]


def blender_cinematic_command(blender_binary, glb, tour, mood, blend, image, report):
    if not Path(glb).is_file() or Path(glb).suffix.lower() != ".glb":
        raise ValueError("existing GLB required")
    if not Path(tour).is_file() or Path(tour).suffix.lower() != ".json":
        raise ValueError("existing camera-tour JSON required")
    if Path(blend).suffix.lower() != ".blend" or Path(image).suffix.lower() != ".png" or Path(report).suffix.lower() != ".json":
        raise ValueError("expect .blend, .png and .json outputs")
    from .shot_design import validate_shot_reel, lighting_recipe
    validate_shot_reel(json.loads(Path(tour).read_text(encoding="utf-8")))
    lighting_recipe(mood=mood)
    if not CINEMATIC.is_file():
        raise FileNotFoundError("Blender cinematic script missing")
    return [str(blender_binary),"--background","--factory-startup", "--python",
            str(CINEMATIC),"--",str(Path(glb).resolve()),str(Path(tour).resolve()),
            mood,str(Path(blend).resolve()),str(Path(image).resolve()),str(Path(report).resolve())]


def blender_material_inspect_command(blender_binary, glb, report):
    if not Path(glb).is_file() or Path(glb).suffix.lower()!=".glb":
        raise ValueError("existing GLB required")
    if Path(report).suffix.lower()!=".json":
        raise ValueError("JSON material report required")
    if not MATERIAL_INSPECT.is_file():
        raise FileNotFoundError("Blender material inspector missing")
    return [str(blender_binary),"--background","--factory-startup","--python",
            str(MATERIAL_INSPECT),"--",str(Path(glb).resolve()),str(Path(report).resolve())]


def blender_director_inspect_command(blender_binary, blend, report):
    if not Path(blend).is_file() or Path(blend).suffix.lower()!=".blend":
        raise ValueError("existing Blender director project required")
    if Path(report).suffix.lower()!=".json":
        raise ValueError("JSON director receipt required")
    return [str(blender_binary),"--background","--factory-startup","--python",
            str(DIRECTOR_INSPECT),"--",str(Path(blend).resolve()),str(Path(report).resolve())]


def blender_director_frames_command(blender_binary, blend, output, report):
    if not Path(blend).is_file() or Path(blend).suffix.lower()!=".blend":
        raise ValueError("existing Blender director .blend required")
    if Path(report).suffix.lower()!=".json":
        raise ValueError("JSON report required")
    if Path(output).exists():
        raise FileExistsError("director frame output must be a new directory")
    return [str(blender_binary),"--background","--factory-startup","--python",
            str(DIRECTOR_FRAMES),"--",str(Path(blend).resolve()),
            str(Path(output).resolve()),str(Path(report).resolve())]


def blender_fx_render_command(blender_binary, glb, image, report, volume_density=0.0, volume_style="uniform"):
    import math
    if type(volume_density) not in (float,int) or not math.isfinite(volume_density) or not 0<=volume_density<=0.25:
        raise ValueError("volume density must be finite and between 0 and 0.25")
    if volume_style not in ("uniform","cloud"):
        raise ValueError("unknown MGR volume style")
    if not Path(glb).is_file() or Path(glb).suffix.lower()!=".glb":
        raise ValueError("existing effect GLB required")
    if Path(image).suffix.lower()!=".png" or Path(report).suffix.lower()!=".json":
        raise ValueError("effect render needs PNG + JSON")
    return [str(blender_binary),"--background","--factory-startup","--python",
            str(FX_RENDER),"--",str(Path(glb).resolve()),
            str(Path(image).resolve()),str(Path(report).resolve()),str(float(volume_density)),volume_style]


def blender_studio_witness_command(blender_binary, blend, image, report):
    """Generate a fresh editable .blend and real CPU-rendered PNG."""
    if (Path(blend).suffix.lower(),Path(image).suffix.lower(),Path(report).suffix.lower())!=(".blend",".png",".json"):
        raise ValueError("studio witness needs .blend, .png and .json")
    if any(Path(path).exists() for path in (blend,image,report)):
        raise FileExistsError("studio witness outputs must all be new")
    if not STUDIO_WITNESS.is_file():
        raise FileNotFoundError("studio witness bridge script missing")
    return [str(blender_binary),"--background","--factory-startup","--python",
            str(STUDIO_WITNESS),"--",str(Path(blend).resolve()),
            str(Path(image).resolve()),str(Path(report).resolve())]
