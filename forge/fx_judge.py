"""MGR FX Judge: measured atmospheric render change at a matched camera.

This does not imply semantic VFX quality or physically correct simulation.
"""

import json
import math
from pathlib import Path

from .visualqa import compare_pngs


def judge_atmosphere(control_image, candidate_image, control_report, candidate_report,
                     *, minimum_rgb_mae=3.0):
    if type(minimum_rgb_mae) not in (int,float) or not math.isfinite(minimum_rgb_mae) or not 0<minimum_rgb_mae<=255:
        raise ValueError("MGR atmosphere change threshold must be finite 0..255")
    a=json.loads(Path(control_report).read_text(encoding="utf-8"))
    b=json.loads(Path(candidate_report).read_text(encoding="utf-8"))
    required=("source","camera","render_engine","render_device","compositor_glare",
              "point_light_count","emission_socket_colors")
    if any(a.get(field)!=b.get(field) for field in required):
        raise ValueError("unmatched render setup; cannot attribute difference to atmosphere")
    if a.get("status")!="PASS" or b.get("status")!="PASS":
        raise ValueError("only valid Blender render receipts may be judged")
    if a.get("volume_density")!=0 or b.get("volume_density",0)<=0:
        raise ValueError("expect zero-density control and positive-density candidate")
    if b.get("volume_shader")!="ShaderNodeVolumePrincipled":
        raise ValueError("candidate must contain verified volumetric shader")
    measured=compare_pngs(control_image,candidate_image)
    delta=measured["rgb_mae"]
    return {"schema":"mgr.forge.fx-atmosphere-judge.v1",
            "status":"PASS" if delta>=minimum_rgb_mae else "FAIL",
            "rgb_mae_8bit":delta,"minimum_rgb_mae_8bit":minimum_rgb_mae,
            "control_sha256":measured["reference_sha256"],
            "candidate_sha256":measured["candidate_sha256"],
            "candidate_density":b["volume_density"],
            "candidate_style":b.get("volume_style","uniform"),
            "limitations":["fixed camera pixel measurement, not cinematic quality judgment",
                           "atmospheric brightness change does not prove smoke dynamics"]}
