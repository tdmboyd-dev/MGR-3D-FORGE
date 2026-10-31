"""Planning boundary for external open-weight 3D models. NO downloads or inference."""
import json
import math
from pathlib import Path

ENGINES_PATH=Path(__file__).resolve().parent/"data"/"generative_engines.json"


def load_engine_profiles(path=ENGINES_PATH):
    doc=json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema")!="mgr.forge.generative-engine-candidates.v1":
        raise ValueError("unsupported generative engine registry")
    profiles=doc.get("engines")
    if not isinstance(profiles,list) or not profiles or len(profiles)>50:
        raise ValueError("invalid generative engine inventory")
    names=set()
    for e in profiles:
        if not isinstance(e,dict) or not isinstance(e.get("id"),str) or e["id"] in names:
            raise ValueError("duplicate/missing generative engine id")
        names.add(e["id"])
        if not isinstance(e.get("tasks"),list) or not e["tasks"]:
            raise ValueError("missing generative tasks")
        if type(e.get("runtime_ready")) is not bool:
            raise ValueError("runtime readiness must be an explicit boolean")
    return profiles


def preflight_generation(engine_id, *, gpu_vram_gb=None, budget_usd=0,
                         weights_available=False, rights_approved=False):
    profiles={entry["id"]:entry for entry in load_engine_profiles()}
    if engine_id not in profiles:
        raise ValueError("unknown generative engine")
    if type(budget_usd) not in (int,float) or not math.isfinite(budget_usd) or budget_usd<0:
        raise ValueError("invalid cost budget")
    if gpu_vram_gb is not None and (type(gpu_vram_gb) not in (int,float) or
                                   not math.isfinite(gpu_vram_gb) or gpu_vram_gb<0):
        raise ValueError("invalid GPU resource")
    if type(weights_available) is not bool or type(rights_approved) is not bool:
        raise ValueError("rights/weights booleans required")
    e=profiles[engine_id]
    blockers=[]
    native=e["id"]=="mgr-native-imagination"
    if not native:
        if not e.get("source_code_present"):
            blockers.append("external backend code not installed in isolated environment")
        if not e.get("model_weights_present") and not weights_available:
            blockers.append("model weights absent; no automatic download")
        if not rights_approved:
            blockers.append("exact model code/weights/dependencies license not accepted")
        need=e.get("min_vram_gb")
        if need is None:
            blockers.append("GPU VRAM requirement not verified")
        elif gpu_vram_gb is None or gpu_vram_gb<need:
            blockers.append("verified GPU VRAM below documented minimum")
        # Zero cloud spend is a valid self-hosted GPU mode; model readiness
        # still requires an installed backend, verified weights and rights.
        # Actual paid-provider dispatch has a separate explicit approval gate.
    return {"engine":engine_id,
            "status":"READY_NATIVE_PROCEDURAL" if native else "ADAPTER_NOT_INSTALLED",
            "can_run_now":native and not blockers,
            "blockers":blockers,
            "hosted_api_usage":False,"model_inference_performed":False,
            "provider_spend_usd":0,
            "notes":"A model profile never substitutes for live inference, saved GLB and independent Blender QA"}
