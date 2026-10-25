"""MGR Forge end-to-end offline scene build, Blender evidence and visual QA.

Deterministic CPU world generation works without Blender. When Blender is
provided, this performs real import and render with independent receipts.
"""

import json
from pathlib import Path
import subprocess

from .blender_bridge import blender_render_command, verify_blender
from .cli import build
from .receipt import file_receipt
from .spec import WorldSpec
from .visualqa import read_png, silhouette, compare_pngs


def run_pipeline(spec: WorldSpec, output, *, blender_binary=None,
                 visual_baseline=None, visual_mae_threshold=0.0):
    """Run stages in a dedicated fresh output directory; never overwrite work."""
    output=Path(output)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise FileExistsError("output must be a fresh or empty dedicated workspace")
    if visual_baseline is not None and blender_binary is None:
        raise ValueError("a Blender render is required to compare a visual baseline")
    world=build(spec,output)
    report={"schema":"mgr.forge.pipeline.v1", "overall":"PARTIAL_CPU_ONLY",
            "stages":{"cpu_world":{"status":"PASS","buildings":len(world["buildings"]),
                                    "glb_sha256":world["artifact"]["sha256"]},
                      "blender_import":{"status":"NOT_RUN"},
                      "blender_render":{"status":"NOT_RUN"},
                      "visual_comparison":{"status":"NOT_RUN"}},
            "limitations":["procedural world only; no neural scene generation",
                           "no semantic visual understanding or active repair loop",
                           "Blender receipt proves only tested file(s) and camera"]}
    destination=output/"pipeline.json"
    try:
        if blender_binary is not None:
            imported=verify_blender(output/"world.glb", output/"blender-import.json",
                                     blender_binary=blender_binary)
            report["stages"]["blender_import"]={"status":"PASS","triangles":imported["triangles"]}
            command=blender_render_command(blender_binary,output/"world.glb",
                                            output/"world-render.png",output/"blender-render.json")
            process=subprocess.run(command,timeout=180,capture_output=True,text=True,check=False)
            if process.returncode:
                raise RuntimeError(f"Blender render failed: {process.stderr[-350:]}")
            render=json.loads((output/"blender-render.json").read_text(encoding="utf-8"))
            if render.get("status")!="PASS":
                raise RuntimeError("Blender render receipt did not pass")
            visual=read_png(output/"world-render.png")
            report["stages"]["blender_render"]={
                "status":"PASS","image":file_receipt(output/"world-render.png"),
                "silhouette":silhouette(visual)}
            if visual_baseline is not None:
                compared=compare_pngs(visual_baseline,output/"world-render.png",
                                     max_mean_absolute_error=visual_mae_threshold)
                report["stages"]["visual_comparison"]={"status":"PASS" if compared["pass"] else "FAIL",
                                                       "comparison":compared}
                if not compared["pass"]:
                    report["overall"]="FAIL_VISUAL_BASELINE"
                else:
                    report["overall"]="PASS_WITH_VISUAL_BASELINE"
            else:
                report["overall"]="PASS_NO_VISUAL_BASELINE"
    except Exception as exc:
        report["overall"]="FAIL"
        report["error"]={"type":type(exc).__name__,"message":str(exc)}
        raise
    finally:
        destination.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return report
